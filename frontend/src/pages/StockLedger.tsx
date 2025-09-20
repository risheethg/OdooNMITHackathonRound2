import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Plus, Search, Package, TrendingUp, TrendingDown } from "lucide-react";

const StockLedger = () => {
  const [searchTerm, setSearchTerm] = useState("");

  const mockProducts = [
    { id: 1, name: "Steel Rod 12mm", type: "Raw Material", stock: 500, unit: "pieces" },
    { id: 2, name: "Electric Motor 5HP", type: "Component", stock: 25, unit: "pieces" },
    { id: 3, name: "Control Panel PCB", type: "Component", stock: 15, unit: "pieces" },
    { id: 4, name: "Steel Frame Assembly", type: "Finished Good", stock: 8, unit: "pieces" },
    { id: 5, name: "Hydraulic Oil", type: "Raw Material", stock: 200, unit: "liters" },
  ];

  const mockMovements = [
    {
      id: 1,
      date: "2024-01-15",
      product: "Steel Rod 12mm",
      type: "Stock In",
      quantity: 100,
      reference: "PO-2024-001",
    },
    {
      id: 2,
      date: "2024-01-14",
      product: "Electric Motor 5HP",
      type: "Stock Out",
      quantity: -5,
      reference: "MO-2024-001",
    },
    {
      id: 3,
      date: "2024-01-13",
      product: "Steel Frame Assembly",
      type: "Stock In",
      quantity: 10,
      reference: "MO-2024-003",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Stock Ledger</h1>
          <p className="text-muted-foreground">Inventory tracking and management</p>
        </div>
        <Button className="bg-gradient-to-r from-primary to-primary-hover">
          <Plus className="h-4 w-4 mr-2" />
          Add New Product
        </Button>
      </div>

      <Card>
        <CardContent className="p-6">
          <Tabs defaultValue="products" className="space-y-6">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="products">Product Master</TabsTrigger>
              <TabsTrigger value="movements">Stock Movements</TabsTrigger>
            </TabsList>

            <TabsContent value="products" className="space-y-4">
              <div className="flex gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search products..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              <div className="rounded-lg border overflow-hidden">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Product Name</th>
                      <th>Product Type</th>
                      <th>Current Stock</th>
                      <th>Unit</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {mockProducts.map((product) => (
                      <tr key={product.id}>
                        <td className="font-medium">{product.name}</td>
                        <td>
                          <Badge variant="outline">
                            {product.type}
                          </Badge>
                        </td>
                        <td className="font-mono">{product.stock}</td>
                        <td>{product.unit}</td>
                        <td>
                          <Badge className={product.stock > 20 ? "status-completed" : 
                                         product.stock > 5 ? "status-progress" : "status-delayed"}>
                            {product.stock > 20 ? "In Stock" : 
                             product.stock > 5 ? "Low Stock" : "Critical"}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </TabsContent>

            <TabsContent value="movements" className="space-y-4">
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
                    {mockMovements.map((movement) => (
                      <tr key={movement.id}>
                        <td>{new Date(movement.date).toLocaleDateString()}</td>
                        <td className="font-medium">{movement.product}</td>
                        <td>
                          <div className="flex items-center gap-2">
                            {movement.type === "Stock In" ? (
                              <TrendingUp className="h-4 w-4 text-success" />
                            ) : (
                              <TrendingDown className="h-4 w-4 text-destructive" />
                            )}
                            <Badge className={movement.type === "Stock In" ? "status-completed" : "status-delayed"}>
                              {movement.type}
                            </Badge>
                          </div>
                        </td>
                        <td className={`font-mono ${movement.quantity > 0 ? "text-success" : "text-destructive"}`}>
                          {movement.quantity > 0 ? "+" : ""}{movement.quantity}
                        </td>
                        <td className="font-mono text-sm">{movement.reference}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default StockLedger;