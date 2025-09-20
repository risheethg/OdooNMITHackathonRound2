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
import { Plus, Search, Filter, MoreHorizontal, Trash2, CheckCircle } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner"; // Assuming a toast library is installed

// --- SELF-CONTAINED MOCKS & SERVICES (to resolve import errors) ---

// 1. Mock Authentication Hook
const useAuth = () => {
  // In a real app, this would come from your auth context (Firebase, Auth0, etc.)
  // For this self-contained component, we'll use a placeholder token.
  return { idToken: "mock-jwt-token-for-development" };
};

// 2. API Service Functions and Types (previously in a separate file)
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export interface ManufacturingOrder {
  _id: string;
  mo_id: string;
  product_id: string;
  quantity: number;
  status: 'planned' | 'progress' | 'completed' | 'delayed';
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
  quantity: number;
}

interface ApiResponse<T> {
  data: T;
  message: string;
  status_code: number;
}

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


// 3. Placeholder Components (to resolve import errors)
const KPICard = ({ title, value, color }) => (
  <Card className={`border-l-4 border-${color}-500`}>
    <CardHeader>
      <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
    </CardHeader>
    <CardContent>
      <p className="text-2xl font-bold">{value}</p>
    </CardContent>
  </Card>
);

const OrdersTable = ({ statusFilter, searchTerm, onDeleteOrder, onCompleteOrder, products }) => {
    const { idToken } = useAuth();
    const { data: orders = [], isLoading, error } = useQuery<ManufacturingOrder[], Error>({
        queryKey: ['manufacturingOrders', statusFilter], // Refetch when filter changes
        queryFn: () => getManufacturingOrders(statusFilter, idToken!),
        enabled: !!idToken,
    });
    
    const productMap = useMemo(() => {
        if (!products) return new Map();
        return new Map(products.map(p => [p._id, p.name]));
    }, [products]);

    const filteredOrders = useMemo(() => {
        if (!orders) return [];
        return orders.filter(order => {
            const productName = productMap.get(order.product_id)?.toLowerCase() || '';
            const search = searchTerm.toLowerCase();
            return (
                order.mo_id.toLowerCase().includes(search) ||
                productName.includes(search)
            );
        });
    }, [orders, searchTerm]);

    if (isLoading) return <div className="text-center p-4">Loading orders...</div>;
    if (error) return <div className="text-center p-4 text-red-500">Error: {error.message}</div>;

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
                    {filteredOrders.map((order) => (
                        <tr key={order._id}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{order.mo_id}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{productMap.get(order.product_id) || order.product_id}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{order.quantity}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-${order.status === 'completed' ? 'green' : 'yellow'}-100 text-${order.status === 'completed' ? 'green' : 'yellow'}-800`}>
                                    {order.status}
                                </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(order.created_at).toLocaleDateString()}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                <Button variant="ghost" size="sm" onClick={() => onCompleteOrder(order.mo_id)} disabled={order.status === 'completed'}>
                                    <CheckCircle className="h-4 w-4 text-green-500" />
                                </Button>
                                <Button variant="ghost" size="sm" onClick={() => onDeleteOrder(order.mo_id)}>
                                    <Trash2 className="h-4 w-4 text-red-500" />
                                </Button>
                            </td>
                        </tr>
                    ))}
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
    enabled: !!idToken, // Fetch products as soon as token is available
  });

  const kpiData = useMemo(() => {
    if (isLoadingKpis) return [];
    const completed = allOrders.filter(o => o.status === 'completed').length;
    const inProgress = allOrders.filter(o => o.status === 'progress').length;
    const delayed = allOrders.filter(o => o.status === 'delayed').length;

    return [
      { title: "Orders Completed", value: completed.toString(), color: "green" },
      { title: "In Progress", value: inProgress.toString(), color: "yellow" },
      { title: "Delayed", value: delayed.toString(), color: "red" },
    ];
  }, [allOrders, isLoadingKpis]);

  const { mutate: deleteOrder } = useMutation({
    mutationFn: (mo_id: string) => deleteManufacturingOrder(mo_id, idToken!),
    onSuccess: () => {
      toast.success("Order deleted successfully!");
      queryClient.invalidateQueries({ queryKey: ['manufacturingOrders'] });
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
    },
    onError: (error) => {
      toast.error(`Failed to complete order: ${error.message}`);
    }
  });

  const { mutate: createOrder, isPending: isCreating } = useMutation({
    mutationFn: (orderData: ManufacturingOrderCreate) => createManufacturingOrder(orderData, idToken!),
    onSuccess: () => {
      toast.success("Manufacturing Order created successfully!");
      queryClient.invalidateQueries({ queryKey: ['manufacturingOrders'] });
      setCreateModalOpen(false); // Close modal on success
    },
    onError: (error) => {
      toast.error(`Failed to create order: ${error.message}`);
    }
  });

  const handleCreateSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const productId = formData.get('product_id') as string;
    const quantity = formData.get('quantity') as string;

    if (!productId || !quantity) {
      toast.error("Please fill out all fields.");
      return;
    }

    createOrder({
      product_id: productId,
      quantity: parseInt(quantity, 10),
    });
  }

  return (
    <div className="space-y-6 p-4 md:p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Manufacturing Orders</h1>
          <p className="text-muted-foreground">Manage and track all manufacturing orders</p>
        </div>
        <Dialog open={isCreateModalOpen} onOpenChange={setCreateModalOpen}>
          <DialogTrigger asChild>
            <Button className="bg-gradient-to-r from-primary to-primary-hover">
              <Plus className="h-4 w-4 mr-2" />
              Create New Order
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Create New Manufacturing Order</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreateSubmit} className="space-y-4">
              <div>
                <label htmlFor="product_id" className="block text-sm font-medium text-gray-700 mb-1">
                  Product
                </label>
                <Select name="product_id" required>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a product to manufacture" />
                  </SelectTrigger>
                  <SelectContent>
                    {isLoadingProducts ? (
                      <SelectItem value="loading" disabled>Loading products...</SelectItem>
                    ) : (
                      products.map(product => (
                        <SelectItem key={product._id} value={product._id}>
                          {product.name}
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">
                  Quantity
                </label>
                <Input
                  id="quantity"
                  name="quantity"
                  type="number"
                  placeholder="e.g., 10"
                  required
                  min="1"
                />
              </div>
              <Button type="submit" className="w-full" disabled={isCreating}>
                {isCreating ? "Creating..." : "Create Order"}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {kpiData.map((kpi, index) => (
          <KPICard key={index} {...kpi} />
        ))}
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
              <Input
                placeholder="Search orders by MO ID or Product Name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="planned">Planned</SelectItem>
                <SelectItem value="progress">In Progress</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="delayed">Delayed</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <OrdersTable 
            searchTerm={searchTerm} 
            statusFilter={statusFilter}
            onDeleteOrder={deleteOrder}
            onCompleteOrder={completeOrder}
            products={products}
          />
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
