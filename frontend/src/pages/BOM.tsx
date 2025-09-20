import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command";
import { Plus, Search, Edit, Trash2, FileText, Package, Settings, X, ChevronsUpDown } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner"; // Assuming you have a toast library like sonner

// --- MOCK AUTH HOOK (Replace with your actual auth context) ---
const useAuth = () => ({ idToken: "mock-jwt-token-for-development" });

// --- API SERVICE AND TYPES (Integrated for self-containment) ---
const API_URL = "http://127.0.0.1:8000";

// Type definitions matching Pydantic models
interface BOMComponent { productId: string; quantity: number; }
interface BOMOperation { name: string; duration: number; }
interface BOM {
  _id: string;
  finishedProductId: string;
  components: BOMComponent[];
  operations: BOMOperation[];
  recipe?: string;
  status?: 'active' | 'draft';
  created_at: string;
  updated_at: string;
}
interface BOMCreate {
  finishedProductId: string;
  components: BOMComponent[];
  operations: BOMOperation[];
  recipe?: string;
}
interface Product {
    _id: string;
    name: string;
}
interface ApiResponse<T> { data: T; message: string; status_code: number; }

// API Functions
const getProducts = async (token: string): Promise<Product[]> => {
    const response = await fetch(`${API_URL}/products/`, { headers: { Authorization: `Bearer ${token}` } });
    if (!response.ok) throw new Error("Failed to fetch products");
    const result: ApiResponse<Product[]> = await response.json();
    return result.data;
};
const getBOMs = async (token: string): Promise<BOM[]> => {
    const response = await fetch(`${API_URL}/boms/`, { headers: { Authorization: `Bearer ${token}` } });
    if (!response.ok) throw new Error("Failed to fetch BOMs");
    const result: ApiResponse<BOM[]> = await response.json();
    return result.data;
};
const createBOM = async (bomData: BOMCreate, token: string): Promise<BOM> => {
    const response = await fetch(`${API_URL}/boms/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(bomData),
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to create BOM");
    }
    const result: ApiResponse<BOM> = await response.json();
    return result.data;
};
const updateBOM = async ({ bomId, bomData, token }: { bomId: string; bomData: BOMCreate; token: string }): Promise<BOM> => {
    const response = await fetch(`${API_URL}/boms/${bomId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(bomData),
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to update BOM");
    }
    const result: ApiResponse<BOM> = await response.json();
    return result.data;
};
const deleteBOM = async ({ bomId, token }: { bomId: string, token: string }): Promise<void> => {
    const response = await fetch(`${API_URL}/boms/${bomId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) throw new Error("Failed to delete BOM");
};

// --- Dialog Components ---
const CreateEditBOMDialog = ({ bom, onClose }: { bom: BOM | null; onClose: () => void }) => {
    const { idToken } = useAuth();
    const queryClient = useQueryClient();
    const [selectedProductId, setSelectedProductId] = useState<string | null>(bom?.finishedProductId || null);
    const [components, setComponents] = useState<BOMComponent[]>(bom?.components || []);
    const [operations, setOperations] = useState<BOMOperation[]>(bom?.operations || []);
    const [finishedProductPopoverOpen, setFinishedProductPopoverOpen] = useState(false);
    const [openComponentPopover, setOpenComponentPopover] = useState<number | null>(null);

    const isEditMode = bom !== null;

    const { data: products = [], isLoading: isLoadingProducts } = useQuery<Product[], Error>({
        queryKey: ["products"],
        queryFn: () => getProducts(idToken!),
        enabled: !!idToken,
    });

    const mutationOptions = {
        onSuccess: () => {
            toast.success(`BOM ${isEditMode ? 'updated' : 'created'} successfully!`);
            queryClient.invalidateQueries({ queryKey: ["boms"] });
            onClose();
        },
        onError: (error: Error) => toast.error(`Error: ${error.message}`),
    };

    const { mutate: createBomMutation, isPending: isCreating } = useMutation({
        mutationFn: (newBom: BOMCreate) => createBOM(newBom, idToken!),
        ...mutationOptions
    });

    const { mutate: updateBomMutation, isPending: isUpdating } = useMutation({
        mutationFn: (vars: { bomId: string, bomData: BOMCreate }) => updateBOM({ ...vars, token: idToken! }),
        ...mutationOptions
    });

    const handleAddComponent = () => setComponents([...components, { productId: "", quantity: 1 }]);
    const handleRemoveComponent = (index: number) => setComponents(components.filter((_, i) => i !== index));
    const handleComponentChange = (index: number, field: keyof BOMComponent, value: string | number) => {
        const newComponents = [...components];
        newComponents[index][field] = value as never;
        setComponents(newComponents);
    };

    const handleAddOperation = () => setOperations([...operations, { name: "", duration: 30 }]);
    const handleRemoveOperation = (index: number) => setOperations(operations.filter((_, i) => i !== index));
    const handleOperationChange = (index: number, field: keyof BOMOperation, value: string | number) => {
        const newOperations = [...operations];
        newOperations[index][field] = value as never;
        setOperations(newOperations);
    };

    const handleSubmit = () => {
        if (!selectedProductId || components.length === 0 || operations.length === 0) {
            toast.warning("Please select a product and add at least one component and operation.");
            return;
        }
        const bomData: BOMCreate = { finishedProductId: selectedProductId, components, operations };
        if (isEditMode) {
            updateBomMutation({ bomId: bom._id, bomData });
        } else {
            createBomMutation(bomData);
        }
    };

    const isPending = isCreating || isUpdating;

    return (
        <DialogContent className="max-w-4xl">
            <DialogHeader><DialogTitle>{isEditMode ? 'Edit' : 'Create New'} Bill of Material</DialogTitle></DialogHeader>
            <div className="space-y-6 py-4">
                <div>
                    <label className="text-sm font-medium">Finished Product</label>
                    <Popover open={finishedProductPopoverOpen} onOpenChange={setFinishedProductPopoverOpen}>
                        <PopoverTrigger asChild>
                            <Button variant="outline" role="combobox" className="w-full justify-between">
                                {selectedProductId ? products.find(p => p._id === selectedProductId)?.name : "Select a product..."}
                                <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                            </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-[--radix-popover-trigger-width] p-0">
                           <Command>
                                <CommandInput placeholder="Search products..." />
                                <CommandEmpty>{isLoadingProducts ? "Loading..." : "No product found."}</CommandEmpty>
                                <CommandList>
                                    <CommandGroup>
                                        {products.map((product) => (
                                            <CommandItem key={product._id} onSelect={() => { setSelectedProductId(product._id); setFinishedProductPopoverOpen(false); }}>
                                                {product.name}
                                            </CommandItem>
                                        ))}
                                    </CommandGroup>
                                </CommandList>
                           </Command>
                        </PopoverContent>
                    </Popover>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card>
                        <CardHeader><CardTitle className="text-lg flex items-center gap-2"><Package className="h-5 w-5" />Required Components</CardTitle></CardHeader>
                        <CardContent className="space-y-2">
                            {components.map((comp, index) => (
                                <div key={index} className="flex gap-2 items-center">
                                    <Popover open={openComponentPopover === index} onOpenChange={(isOpen) => setOpenComponentPopover(isOpen ? index : null)}>
                                        <PopoverTrigger asChild>
                                            <Button variant="outline" role="combobox" className="w-full justify-between font-normal">
                                                {comp.productId ? products.find(p => p._id === comp.productId)?.name : "Select component..."}
                                                <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                                            </Button>
                                        </PopoverTrigger>
                                        <PopoverContent className="w-[--radix-popover-trigger-width] p-0">
                                            <Command>
                                                <CommandInput placeholder="Search products..." />
                                                <CommandEmpty>{isLoadingProducts ? "Loading..." : "No product found."}</CommandEmpty>
                                                <CommandList>
                                                    <CommandGroup>
                                                        {products.map((product) => (
                                                            <CommandItem key={product._id} onSelect={() => { handleComponentChange(index, 'productId', product._id); setOpenComponentPopover(null); }}>
                                                                {product.name}
                                                            </CommandItem>
                                                        ))}
                                                    </CommandGroup>
                                                </CommandList>
                                            </Command>
                                        </PopoverContent>
                                    </Popover>
                                    <Input type="number" placeholder="Qty" value={comp.quantity} onChange={(e) => handleComponentChange(index, 'quantity', parseInt(e.target.value) || 0)} className="w-24" />
                                    <Button variant="ghost" size="icon" onClick={() => handleRemoveComponent(index)}><X className="h-4 w-4" /></Button>
                                </div>
                            ))}
                            <Button variant="outline" size="sm" className="w-full mt-2" onClick={handleAddComponent}><Plus className="h-4 w-4 mr-1" />Add Component</Button>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader><CardTitle className="text-lg flex items-center gap-2"><Settings className="h-5 w-5" />Manufacturing Operations</CardTitle></CardHeader>
                        <CardContent className="space-y-2">
                            {operations.map((op, index) => (
                                <div key={index} className="flex gap-2 items-center">
                                    <Input placeholder="Operation Name" value={op.name} onChange={(e) => handleOperationChange(index, 'name', e.target.value)} />
                                    <Input type="number" placeholder="Mins" value={op.duration} onChange={(e) => handleOperationChange(index, 'duration', parseInt(e.target.value) || 0)} className="w-24" />
                                    <Button variant="ghost" size="icon" onClick={() => handleRemoveOperation(index)}><X className="h-4 w-4" /></Button>
                                </div>
                            ))}
                            <Button variant="outline" size="sm" className="w-full mt-2" onClick={handleAddOperation}><Plus className="h-4 w-4 mr-1" />Add Operation</Button>
                        </CardContent>
                    </Card>
                </div>
                <div className="flex justify-end gap-2">
                    <Button variant="outline" onClick={onClose}>Cancel</Button>
                    <Button onClick={handleSubmit} disabled={isPending}>{isPending ? "Saving..." : "Save BOM"}</Button>
                </div>
            </div>
        </DialogContent>
    );
};

const ViewBOMDialog = ({ bom, products, onClose }: { bom: BOM; products: Product[]; onClose: () => void }) => {
    const getProductName = (productId: string) => products.find(p => p._id === productId)?.name || productId;

    return (
        <DialogContent className="max-w-2xl">
            <DialogHeader><DialogTitle>BOM Details: {getProductName(bom.finishedProductId)}</DialogTitle></DialogHeader>
            <div className="space-y-6 py-4">
                 <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card>
                        <CardHeader><CardTitle className="text-lg flex items-center gap-2"><Package className="h-5 w-5" />Components</CardTitle></CardHeader>
                        <CardContent>
                            <ul className="space-y-2">
                                {bom.components.map((c, i) => <li key={i} className="flex justify-between"><span>{getProductName(c.productId)}</span> <strong>{c.quantity}</strong></li>)}
                            </ul>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader><CardTitle className="text-lg flex items-center gap-2"><Settings className="h-5 w-5" />Operations</CardTitle></CardHeader>
                        <CardContent>
                            <ul className="space-y-2">
                                {bom.operations.map((o, i) => <li key={i} className="flex justify-between"><span>{o.name}</span> <strong>{o.duration} mins</strong></li>)}
                            </ul>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </DialogContent>
    )
}

// --- MAIN BOM COMPONENT ---
const BOM = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [selectedBOM, setSelectedBOM] = useState<BOM | null>(null);
  const { idToken } = useAuth();
  const queryClient = useQueryClient();

  const { data: products = [] } = useQuery<Product[], Error>({ queryKey: ["products"], queryFn: () => getProducts(idToken!), enabled: !!idToken });
  const { data: boms = [], isLoading, error } = useQuery<BOM[], Error>({ queryKey: ["boms"], queryFn: () => getBOMs(idToken!), enabled: !!idToken });

  const { mutate: deleteBomMutation } = useMutation({
      mutationFn: (bomId: string) => deleteBOM({ bomId, token: idToken! }),
      onSuccess: () => {
          toast.success("BOM deleted successfully!");
          queryClient.invalidateQueries({ queryKey: ["boms"] });
      },
      onError: (error) => toast.error(`Error: ${error.message}`),
  });

  const handleOpenDialog = (bom: BOM | null) => {
      setSelectedBOM(bom);
      setDialogOpen(true);
  }
  const handleOpenViewDialog = (bom: BOM) => {
      setSelectedBOM(bom);
      setViewDialogOpen(true);
  }

  const filteredBOMs = boms.filter(bom =>
    (products.find(p => p._id === bom.finishedProductId)?.name || bom.finishedProductId).toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Bills of Material</h1>
          <p className="text-muted-foreground">Manage product recipes and manufacturing processes</p>
        </div>
        <Button className="bg-gradient-to-r from-primary to-primary-hover" onClick={() => handleOpenDialog(null)}>
          <Plus className="h-4 w-4 mr-2" />
          Create New BOM
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Bill of Materials List</CardTitle>
          <CardDescription>A list of all product recipes in the system.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by Finished Product name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
            {isLoading && <p>Loading BOMs...</p>}
            {error && <p className="text-destructive">Error: {error.message}</p>}
            {!isLoading && !error && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredBOMs.map((bom) => (
                  <Card key={bom._id} className="hover:shadow-lg transition-shadow duration-300 flex flex-col">
                    <CardHeader>
                        <div className="flex items-start justify-between">
                            <CardTitle className="text-lg">{products.find(p => p._id === bom.finishedProductId)?.name || bom.finishedProductId}</CardTitle>
                            <Badge variant={bom.status === "active" ? "default" : "secondary"}>{bom.status || 'draft'}</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground pt-1">ID: {bom.finishedProductId}</p>
                    </CardHeader>
                    <CardContent className="space-y-4 flex-grow">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Components:</span>
                        <span className="font-medium">{bom.components.length}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Operations:</span>
                        <span className="font-medium">{bom.operations.length}</span>
                      </div>
                    </CardContent>
                    <div className="p-4 pt-0 mt-auto">
                        <div className="flex gap-2 border-t pt-4">
                            <Button size="sm" variant="outline" onClick={() => handleOpenViewDialog(bom)}><FileText className="h-4 w-4 mr-1" />View</Button>
                            <Button size="sm" variant="outline" onClick={() => handleOpenDialog(bom)}><Edit className="h-4 w-4 mr-1" />Edit</Button>
                            <Button size="sm" variant="destructive" onClick={() => deleteBomMutation(bom._id)}><Trash2 className="h-4 w-4 mr-1" />Delete</Button>
                        </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
        </CardContent>
      </Card>
      
      {dialogOpen && <Dialog open={dialogOpen} onOpenChange={setDialogOpen}><CreateEditBOMDialog bom={selectedBOM} onClose={() => setDialogOpen(false)} /></Dialog>}
      {viewDialogOpen && <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}><ViewBOMDialog bom={selectedBOM!} products={products} onClose={() => setViewDialogOpen(false)} /></Dialog>}

    </div>
  );
};

export default BOM;

