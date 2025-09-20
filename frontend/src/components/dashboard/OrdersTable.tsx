import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Edit, Trash2, Eye, Circle } from "lucide-react";
import { cn } from "@/lib/utils";

interface OrdersTableProps {
  searchTerm: string;
  statusFilter: string;
}

const mockOrders = [
  {
    id: "MO-2024-001",
    product: "Steel Frame Assembly",
    quantity: 50,
    scheduledDate: "2024-01-15",
    assignee: "John Smith",
    componentAvailability: "available",
    status: "progress",
  },
  {
    id: "MO-2024-002",
    product: "Electric Motor Unit",
    quantity: 25,
    scheduledDate: "2024-01-18",
    assignee: "Sarah Johnson",
    componentAvailability: "not-available",
    status: "planned",
  },
  {
    id: "MO-2024-003",
    product: "Control Panel Board",
    quantity: 15,
    scheduledDate: "2024-01-10",
    assignee: "Mike Wilson",
    componentAvailability: "available",
    status: "completed",
  },
  {
    id: "MO-2024-004",
    product: "Hydraulic Cylinder",
    quantity: 30,
    scheduledDate: "2024-01-12",
    assignee: "Lisa Chen",
    componentAvailability: "available",
    status: "delayed",
  },
  {
    id: "MO-2024-005",
    product: "Gear Box Assembly",
    quantity: 20,
    scheduledDate: "2024-01-20",
    assignee: "David Brown",
    componentAvailability: "available",
    status: "planned",
  },
];

const getStatusBadge = (status: string) => {
  const statusConfig = {
    planned: { label: "Planned", className: "status-planned" },
    progress: { label: "In Progress", className: "status-progress" },
    completed: { label: "Completed", className: "status-completed" },
    delayed: { label: "Delayed", className: "status-delayed" },
  };

  const config = statusConfig[status as keyof typeof statusConfig];
  return (
    <Badge className={cn("status-badge", config.className)}>
      {config.label}
    </Badge>
  );
};

const getAvailabilityIndicator = (availability: string) => {
  return (
    <div className="flex items-center gap-2">
      <Circle 
        className={cn("h-3 w-3 fill-current", 
          availability === "available" ? "text-success" : "text-destructive"
        )} 
      />
      <span className="text-sm">
        {availability === "available" ? "Available" : "Not Available"}
      </span>
    </div>
  );
};

const OrdersTable = ({ searchTerm, statusFilter }: OrdersTableProps) => {
  const filteredOrders = mockOrders.filter((order) => {
    const matchesSearch = order.product.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         order.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         order.assignee.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === "all" || order.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="rounded-lg border overflow-hidden">
      <table className="data-table">
        <thead>
          <tr>
            <th>Order ID</th>
            <th>Product Name</th>
            <th>Quantity</th>
            <th>Scheduled Date</th>
            <th>Assignee</th>
            <th>Component Availability</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filteredOrders.map((order) => (
            <tr key={order.id}>
              <td className="font-mono text-sm font-medium">{order.id}</td>
              <td className="font-medium">{order.product}</td>
              <td>{order.quantity}</td>
              <td>{new Date(order.scheduledDate).toLocaleDateString()}</td>
              <td>{order.assignee}</td>
              <td>{getAvailabilityIndicator(order.componentAvailability)}</td>
              <td>{getStatusBadge(order.status)}</td>
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
      
      {filteredOrders.length === 0 && (
        <div className="text-center py-8 text-muted-foreground">
          No orders found matching your criteria.
        </div>
      )}
    </div>
  );
};

export { OrdersTable };