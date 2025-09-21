import React, { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Plus, Search, Filter, Trash2, CheckCircle } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

// --- SELF-CONTAINED MOCKS & SERVICES ---

const useAuth = () => {
  return { idToken: "mock-jwt-token-for-development" };
};

const API_URL = "http://127.0.0.1:8000";

// --- DATA INTERFACES ---
export interface ManufacturingOrder {
  _id: string;
  mo_id: string;
  product_id: string;
  quantity_to_produce: number;
  status: 'planned' | 'in_progress' | 'done' | 'cancelled';
  created_at: string;
  updated_at: string;
}

export interface Product {
  _id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface ManufacturingOrderCreate {
  product_id: string;
  quantity: number; // FIX: Reverted to 'quantity' to match backend expectation
}

export interface ProductCreate {
  name: string;
  type: 'Raw Material' | 'Finished Good';
  description?: string;
}

interface ApiResponse<T> {
  data: T;
  message: string;
  status_code: number;
}

// --- API SERVICE FUNCTIONS ---

export const getManufacturingOrders = async (status: string, token: string): Promise<ManufacturingOrder[]> => {
  let url = `${API_URL}/manufacturing-orders/`;
  if (status && status !== 'all') {
    url += `?status=${status}`;
  }
  const response = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.message || 'Failed to fetch orders');
  }
  const result: ApiResponse<ManufacturingOrder[]> = await response.json();
  return result.data;
};

export const deleteManufacturingOrder = async (mo_id: string, token: string): Promise<void> => {
  const response = await fetch(`${API_URL}/manufacturing-orders/${mo_id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.message || 'Failed to delete order');
  }
};

export const completeManufacturingOrder = async (mo_id: string, token: string): Promise<any> => {
    const response = await fetch(`${API_URL}/manufacturing-orders/${mo_id}/complete`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to complete order');
    }
    const result: ApiResponse<any> = await response.json();
    return result.data;
};

export const createManufacturingOrder = async (orderData: ManufacturingOrderCreate, token: string): Promise<ManufacturingOrder> => {
  const response = await fetch(`${API_URL}/manufacturing-orders/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(orderData),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.message || 'Failed to create order');
  }
  const result: ApiResponse<ManufacturingOrder> = await response.json();
  return result.data;
};

export const getProducts = async (token: string): Promise<Product[]> => {
  const response = await fetch(`${API_URL}/products/`, { headers: { Authorization: `Bearer ${token}` } });
  if (!response.ok) {
    throw new Error('Failed to fetch products');
  }
  const result: ApiResponse<Product[]> = await response.json();
  return result.data;
}

export const createProduct = async (productData: ProductCreate, token: string): Promise<Product> => {
  const response = await fetch(`${API_URL}/products/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(productData),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.message || 'Failed to create product');
  }
  const result: ApiResponse<Product> = await response.json();
  return result.data;
};


// --- UI COMPONENTS ---

const KPICard = ({ title, value }) => (
  <Card>
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">{title}</CardTitle>
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold">{value}</div>
    </CardContent>
  </Card>
);


const OrdersTable = ({ statusFilter, searchTerm, onDeleteOrder, onCompleteOrder, products }) => {
    const { idToken } = useAuth();
    const { data: orders = [], isLoading, error } = useQuery<ManufacturingOrder[], Error>({
        queryKey: ['manufacturingOrders', statusFilter],
        queryFn: () => getManufacturingOrders(statusFilter, idToken!),
        enabled: !!idToken,
    });
    
    const productMap = useMemo(() => {
        if (!products) return new Map();
        return new Map(products.map(p => [p._id, p.name]));
    }, [products]);

    const filteredOrders = useMemo(() => {
        if (!orders) return [];
        
        const searchLower = (searchTerm || '').toLowerCase();
        
        return orders.filter(order => {
            if (!order) return false;
            
            const productName = (productMap.get(order.product_id) || '').toLowerCase();
            const moId = (order.mo_id || '').toLowerCase();
    
            return moId.includes(searchLower) || productName.includes(searchLower);
        });
    }, [orders, searchTerm, productMap]);

    if (isLoading) return <div className="text-center p-4">Loading orders...</div>;
    if (error) return <div className="text-center p-4 text-red-500">Error: {error.message}</div>;

    const getStatusColor = (status: ManufacturingOrder['status']) => {
        switch (status) {
            case 'done': return 'green';
            case 'in_progress': return 'yellow';
            case 'cancelled': return 'red';
            case 'planned':
            default: return 'blue';
        }
    };

    return (
        <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                    <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">MO ID</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created At</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    {filteredOrders.length > 0 ? filteredOrders.map((order) => {
                        const statusColor = getStatusColor(order.status);
                        return (
                            <tr key={order._id}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{order.mo_id}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{productMap.get(order.product_id) || 'Unknown Product'}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{order.quantity_to_produce}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-${statusColor}-100 text-${statusColor}-800`}>
                                        {order.status}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(order.created_at).toLocaleDateString()}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-1">
                                    <Button variant="ghost" size="sm" onClick={() => onCompleteOrder(order.mo_id)} disabled={order.status === 'done'}>
                                        <CheckCircle className="h-4 w-4 text-green-500" />
                                    </Button>
                                    <Button variant="ghost" size="sm" onClick={() => onDeleteOrder(order.mo_id)}>
                                        <Trash2 className="h-4 w-4 text-red-500" />
                                    </Button>
                                </td>
                            </tr>
                        );
                    }) : (
                        <tr>
                            <td colSpan={6} className="text-center py-10 text-gray-500">No manufacturing orders found.</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
};

// --- MAIN DASHBOARD COMPONENT ---

const Dashboard = () => {
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [isCreateModalOpen, setCreateModalOpen] = useState(false);
  const [isCreateProductModalOpen, setCreateProductModalOpen] = useState(false);
  const { idToken } = useAuth();
  const queryClient = useQueryClient();

  const { data: allOrders = [], isLoading: isLoadingKpis } = useQuery<ManufacturingOrder[], Error>({
    queryKey: ['manufacturingOrders', 'all-for-kpi'],
    queryFn: () => getManufacturingOrders('all', idToken!),
    enabled: !!idToken,
  });

  const { data: products = [], isLoading: isLoadingProducts } = useQuery<Product[], Error>({
    queryKey: ['products'],
    queryFn: () => getProducts(idToken!),
    enabled: !!idToken,
  });

  const kpiData = useMemo(() => {
    if (isLoadingKpis || !allOrders) return [
      { title: "Orders Completed", value: "0" },
      { title: "In Progress", value: "0" },
      { title: "Cancelled", value: "0" },
    ];
    const completed = allOrders.filter(o => o.status === 'done').length;
    const inProgress = allOrders.filter(o => o.status === 'in_progress').length;
    const cancelled = allOrders.filter(o => o.status === 'cancelled').length;

    return [
      { title: "Orders Completed", value: completed.toString() },
      { title: "In Progress", value: inProgress.toString() },
      { title: "Cancelled", value: cancelled.toString() },
    ];
  }, [allOrders, isLoadingKpis]);

  const { mutate: deleteOrder } = useMutation({
    mutationFn: (mo_id: string) => deleteManufacturingOrder(mo_id, idToken!),
    onSuccess: () => {
      toast.success("Order deleted successfully!");
      queryClient.invalidateQueries({ queryKey: ['manufacturingOrders'] });
      queryClient.invalidateQueries({ queryKey: ['manufacturingOrders', 'all-for-kpi'] });
    },
    onError: (error) => {
      toast.error(`Failed to delete order: ${error.message}`);
    }
  });

  const { mutate: completeOrder } = useMutation({
    mutationFn: (mo_id: string) => completeManufacturingOrder(mo_id, idToken!),
    onSuccess: () => {
      toast.success("Order marked as complete!");
      queryClient.invalidateQueries({ queryKey: ['manufacturingOrders'] });
      queryClient.invalidateQueries({ queryKey: ['manufacturingOrders', 'all-for-kpi'] });
    },
    onError: (error) => {
      toast.error(`Failed to complete order: ${error.message}`);
    }
  });

  const { mutate: createOrder, isPending: isCreating } = useMutation<ManufacturingOrder, Error, ManufacturingOrderCreate>({
    mutationFn: (orderData: ManufacturingOrderCreate) => createManufacturingOrder(orderData, idToken!),
    onSuccess: (data) => {
      // The backend now returns the full MO object, including the new mo_id
      toast.success(`Order ${data.mo_id} created successfully!`);
      queryClient.invalidateQueries({ queryKey: ['manufacturingOrders'] });
      queryClient.invalidateQueries({ queryKey: ['manufacturingOrders', 'all-for-kpi'] });
      setCreateModalOpen(false);
    },
    onError: (error) => {
      toast.error(`Failed to create order: ${error.message}`);
    }
  });

  const handleCreateSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const productId = formData.get('product_id') as string;
    const quantityStr = formData.get('quantity') as string; // FIX: Changed to get correct form field

    if (!productId || !quantityStr || parseInt(quantityStr, 10) <= 0) {
      toast.error("Please fill out all fields.");
      return;
    }
    
    createOrder({
      product_id: productId,
      quantity: parseInt(quantityStr, 10), // FIX: Changed to send correct field name
    });
  }

  const { mutate: createNewProduct, isPending: isCreatingProduct } = useMutation({
    mutationFn: (productData: ProductCreate) => createProduct(productData, idToken!),
    onSuccess: () => {
      toast.success("Product created successfully!");
      queryClient.invalidateQueries({ queryKey: ['products'] });
      setCreateProductModalOpen(false);
    },
    onError: (error) => {
      toast.error(`Failed to create product: ${error.message}`);
    }
  });

  const handleCreateProductSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const name = formData.get('name') as string;
    const type = formData.get('type') as 'Raw Material' | 'Finished Good';
    const description = formData.get('description') as string;

    if (!name || !type) {
      toast.error("Product Name and Type are required.");
      return;
    }

    createNewProduct({ name, type, description });
  };

  return (
    <div className="space-y-6 p-4 md:p-6 bg-gray-50/50 min-h-screen">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Manufacturing Orders</h1>
          <p className="text-muted-foreground">Manage and track all manufacturing orders</p>
        </div>
        <div className="flex gap-2">
          <Dialog open={isCreateProductModalOpen} onOpenChange={setCreateProductModalOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Plus className="h-4 w-4 mr-2" />
                Create Product
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader><DialogTitle>Create New Product</DialogTitle></DialogHeader>
              <form onSubmit={handleCreateProductSubmit} className="space-y-4 pt-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">Product Name</label>
                  <Input id="name" name="name" placeholder="e.g., Wooden Table" required />
                </div>
                <div>
                  <label htmlFor="type" className="block text-sm font-medium text-gray-700 mb-1">Product Type</label>
                  <Select name="type" required><SelectTrigger><SelectValue placeholder="Select a product type" /></SelectTrigger><SelectContent><SelectItem value="Finished Good">Finished Good</SelectItem><SelectItem value="Raw Material">Raw Material</SelectItem></SelectContent></Select>
                </div>
                <div>
                  <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">Description (Optional)</label>
                  <Input id="description" name="description" placeholder="e.g., A sturdy oak dining table" />
                </div>
                <Button type="submit" className="w-full" disabled={isCreatingProduct}>{isCreatingProduct ? "Creating..." : "Create Product"}</Button>
              </form>
            </DialogContent>
          </Dialog>

          <Dialog open={isCreateModalOpen} onOpenChange={setCreateModalOpen}>
            <DialogTrigger asChild><Button><Plus className="h-4 w-4 mr-2" />Create New Order</Button></DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader><DialogTitle>Create New Manufacturing Order</DialogTitle></DialogHeader>
              <form onSubmit={handleCreateSubmit} className="space-y-4 pt-4">
                <div>
                  <label htmlFor="product_id" className="block text-sm font-medium text-gray-700 mb-1">Product</label>
                  <Select name="product_id" required><SelectTrigger><SelectValue placeholder="Select a product" /></SelectTrigger><SelectContent>{isLoadingProducts ? (<SelectItem value="loading" disabled>Loading...</SelectItem>) : (products.map(p => (<SelectItem key={p._id} value={p._id}>{p.name}</SelectItem>)))}</SelectContent></Select>
                </div>
                <div>
                  {/* FIX: Changed name and id back to 'quantity' */}
                  <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
                  <Input id="quantity" name="quantity" type="number" placeholder="e.g., 10" required min="1" />
                </div>
                <Button type="submit" className="w-full" disabled={isCreating}>{isCreating ? "Creating..." : "Create Order"}</Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {kpiData.map((kpi, index) => ( <KPICard key={index} {...kpi} /> ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Order Management</CardTitle>
          <CardDescription>View, search, and filter all manufacturing orders.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search by MO ID or Product Name..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-48"><Filter className="h-4 w-4 mr-2" /><SelectValue placeholder="Filter by status" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="planned">Planned</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="done">Done</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <OrdersTable searchTerm={searchTerm} statusFilter={statusFilter} onDeleteOrder={deleteOrder} onCompleteOrder={completeOrder} products={products} />
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
