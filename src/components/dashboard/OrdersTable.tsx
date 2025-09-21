import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Edit, Trash2, Eye, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useQuery } from "@tanstack/react-query";
import { getManufacturingOrders, ManufacturingOrder } from "@/services/manufacturingOrders";
import { useAuth } from "@/Root";

interface OrdersTableProps {
  searchTerm: string;
  statusFilter: string;
}

const OrdersTable = ({ searchTerm, statusFilter }: OrdersTableProps) => {
  const { idToken } = useAuth();

  const { data: orders, isLoading, error } = useQuery<ManufacturingOrder[], Error>({
    queryKey: ['manufacturingOrders', statusFilter, searchTerm],
    queryFn: () => getManufacturingOrders(statusFilter, searchTerm, idToken!),
    enabled: !!idToken,
  });

  if (isLoading) {
    return <div className="flex justify-center items-center h-40"><Loader2 className="h-8 w-8 animate-spin text-primary" /></div>;
  }

  if (error) {
    return <div className="text-center text-destructive py-8">Error: {error.message}</div>;
  }

  return (
    <div className="rounded-lg border overflow-hidden">
      <table className="data-table">
        <thead>
          <tr>
            <th>Product Name</th>
            <th>BOM ID</th>
            <th>Quantity</th>
            <th>Created At</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {orders?.map((order) => (
            <tr key={order._id}>
              <td className="font-medium">{order.productName}</td>
              <td className="font-mono text-sm">{order.bomId}</td>
              <td>{order.quantity}</td>
              <td>{new Date(order.createdAt).toLocaleDateString()}</td>
              <td>
                <Badge
                  className={cn(
                    "status-badge",
                    order.status === "progress" ? "status-progress" :
                    order.status === "planned" ? "status-planned" :
                    order.status === "completed" ? "status-completed" :
                    "status-delayed"
                  )}
                >
                  {order.status}
                </Badge>
              </td>
              <td>
                <div className="flex items-center gap-1">
                  <Button variant="ghost" size="sm">
                    <Eye className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" className="text-destructive hover:text-destructive">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      
      {orders?.length === 0 && (
        <div className="text-center py-8 text-muted-foreground">
          No orders found matching your criteria.
        </div>
      )}
    </div>
  );
};

export { OrdersTable };