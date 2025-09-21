import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Plus, Search, TrendingUp, TrendingDown } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/Root"; // Assuming useAuth is in Root

// --- API SERVICE AND TYPES ---
const API_URL = "http://127.0.0.1:8000";

interface ApiResponse<T> {
  data: T;
  message: string;
  status_code: number;
}

interface Product {
  _id: string;
  name: string;
  type: 'Raw Material' | 'Finished Good';
}

interface StockAvailability {
  product_id: string;
  product_name: string;
  product_type: 'Raw Material' | 'Finished Good';
  current_stock: number;
}

interface StockMovement {
  _id: string;
  product_id: string;
  quantity_change: number;
  timestamp: string;
  reason: string;
  manufacturing_order_id?: string;
}

const getStockAvailability = async (token: string): Promise<StockAvailability[]> => {
  const res = await fetch(`${API_URL}/stock-ledger/availability`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error("Failed to fetch stock availability");
  const result: ApiResponse<StockAvailability[]> = await res.json();
  return result.data;
};

const getStockMovements = async (token: string): Promise<StockMovement[]> => {
  const res = await fetch(`${API_URL}/stock-ledger/`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error("Failed to fetch stock movements");
  const result: ApiResponse<StockMovement[]> = await res.json();
  return result.data;
};

const getProducts = async (token: string): Promise<Product[]> => {
  const res = await fetch(`${API_URL}/products/`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error("Failed to fetch products");
  const result: ApiResponse<Product[]> = await res.json();
  return result.data;
};

const StockLedger = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const { idToken } = useAuth();

  const { data: availability = [], isLoading: isLoadingAvailability } = useQuery<StockAvailability[], Error>({
    queryKey: ['stockAvailability'],
    queryFn: () => getStockAvailability(idToken!),
    enabled: !!idToken,
  });

  const { data: movements = [], isLoading: isLoadingMovements } = useQuery<StockMovement[], Error>({
    queryKey: ['stockMovements'],
    queryFn: () => getStockMovements(idToken!),
    enabled: !!idToken,
  });

  const { data: products = [] } = useQuery<Product[], Error>({
    queryKey: ['products'],
    queryFn: () => getProducts(idToken!),
    enabled: !!idToken,
  });

  const productMap = useMemo(() => new Map(products.map(p => [p._id, p.name])), [products]);

  const filteredAvailability = useMemo(() =>
    availability.filter(p =>
      p.product_name.toLowerCase().includes(searchTerm.toLowerCase())
    ), [availability, searchTerm]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Stock Ledger</h1>
          <p className="text-muted-foreground">Inventory tracking and management</p>
        </div>
      </div>

      <Card>
        <CardContent className="p-6">
          <Tabs defaultValue="products" className="space-y-6">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="products">Current Stock</TabsTrigger>
              <TabsTrigger value="movements">Stock Movements</TabsTrigger>
            </TabsList>

            <TabsContent value="products" className="space-y-4">
              <div className="flex gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search by product name..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              {isLoadingAvailability ? <p>Loading stock levels...</p> : (
                <div className="rounded-lg border overflow-hidden">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Product Name</th>
                        <th>Product Type</th>
                        <th>Current Stock</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredAvailability.map((product) => (
                        <tr key={product.product_id}>
                          <td className="font-medium">{product.product_name}</td>
                          <td><Badge variant="outline">{product.product_type}</Badge></td>
                          <td className="font-mono">{product.current_stock}</td>
                          <td>
                            <Badge className={product.current_stock > 20 ? "status-completed" : product.current_stock > 0 ? "status-progress" : "status-delayed"}>
                              {product.current_stock > 20 ? "In Stock" : product.current_stock > 0 ? "Low Stock" : "Out of Stock"}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </TabsContent>

            <TabsContent value="movements" className="space-y-4">
              {isLoadingMovements ? <p>Loading movements...</p> : (
                <div className="rounded-lg border overflow-hidden">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Product</th>
                        <th>Type</th>
                        <th>Quantity</th>
                        <th>Reference</th>
                      </tr>
                    </thead>
                    <tbody>
                      {movements.map((movement) => (
                        <tr key={movement._id}>
                          <td>{new Date(movement.timestamp).toLocaleString()}</td>
                          <td className="font-medium">{productMap.get(movement.product_id) || movement.product_id}</td>
                          <td>
                            <div className="flex items-center gap-2">
                              {movement.quantity_change > 0 ? (
                                <TrendingUp className="h-4 w-4 text-success" />
                              ) : (
                                <TrendingDown className="h-4 w-4 text-destructive" />
                              )}
                              <Badge className={movement.quantity_change > 0 ? "status-completed" : "status-delayed"}>
                                {movement.quantity_change > 0 ? "Stock In" : "Stock Out"}
                              </Badge>
                            </div>
                          </td>
                          <td className={`font-mono ${movement.quantity_change > 0 ? "text-success" : "text-destructive"}`}>
                            {movement.quantity_change > 0 ? "+" : ""}{movement.quantity_change}
                          </td>
                          <td className="font-mono text-sm">{movement.reason}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default StockLedger;