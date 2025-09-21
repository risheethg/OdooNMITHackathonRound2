import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { ClipboardList, Play, Pause, CheckCircle, Search, Filter } from "lucide-react";
import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useAuth } from "@/Root";

// --- API Service Functions ---

const API_URL = "http://127.0.0.1:8000";

export interface WorkOrder {
  _id: string;
  name: string;
  manufacturingOrderId: string;
  status: 'Planned' | 'In Progress' | 'Paused' | 'Completed' | 'Canceled';
  expectedDuration: number;
  workCenterId?: string;
}

export interface WorkCenter {
  _id: string;
  name: string;
  code: string;
}

export const getWorkOrders = async (token: string): Promise<WorkOrder[]> => {
  const response = await fetch(`${API_URL}/api/work-orders/`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!response.ok) throw new Error('Failed to fetch work orders');
  const result = await response.json();
  return result.data;
};

export const getWorkCenters = async (token: string): Promise<WorkCenter[]> => {
  const response = await fetch(`${API_URL}/api/work-centres/`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!response.ok) throw new Error('Failed to fetch work centers');
  const result = await response.json();
  return result.data;
};

export const updateWorkOrderStatus = async ({ wo_id, status, token }: { wo_id: string; status: WorkOrder['status']; token: string }): Promise<any> => {
  const response = await fetch(`${API_URL}/api/work-orders/${wo_id}/status`, {
    method: 'PATCH',
    headers: { 
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ status }),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to update work order status');
  }
  return response.json();
};

const WorkOrders = () => {
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const token = localStorage.getItem('access_token');

  const { data: workOrders = [], isLoading, error } = useQuery<WorkOrder[], Error>({
    queryKey: ['workOrders'],
    queryFn: () => getWorkOrders(token!),
    enabled: !!token,
  });

  const { data: workCenters = [] } = useQuery<WorkCenter[], Error>({
    queryKey: ['workCenters'],
    queryFn: () => getWorkCenters(token!),
    enabled: !!token,
  });

  const workCenterMap = useMemo(() => new Map(workCenters.map(wc => [wc._id, wc.name])), [workCenters]);

  const { mutate: updateStatus, isPending: isUpdatingStatus } = useMutation({
    mutationFn: ({ wo_id, status }: { wo_id: string; status: WorkOrder['status'] }) => 
      updateWorkOrderStatus({ wo_id, status, token: token! }),
    onSuccess: () => {
      toast.success("Work order status updated!");
      queryClient.invalidateQueries({ queryKey: ['workOrders'] });
    },
    onError: (e: Error) => {
      toast.error(`Failed to update status: ${e.message}`);
    }
  });

  const filteredWorkOrders = useMemo(() => {
    return workOrders.filter(order => {
      const searchLower = searchTerm.toLowerCase();
      const statusMatch = statusFilter === 'all' || order.status.toLowerCase().replace(/ /g, '-') === statusFilter;
      const searchMatch =
        order.name.toLowerCase().includes(searchLower) ||
        order.manufacturingOrderId.toLowerCase().includes(searchLower) ||
        (workCenterMap.get(order.workCenterId || '') || '').toLowerCase().includes(searchLower);
      return statusMatch && searchMatch;
    });
  }, [workOrders, searchTerm, statusFilter, workCenterMap]);

  const getStatusBadgeClass = (status: WorkOrder['status']) => {
    switch (status) {
      case 'In Progress': return 'status-progress';
      case 'Paused': return 'status-planned';
      case 'Completed': return 'status-completed';
      case 'Canceled': return 'status-delayed';
      case 'Planned':
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) return <div className="text-center p-8">Loading work orders...</div>;
  if (error) return <div className="text-center p-8 text-destructive">Error: {error.message}</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Work Orders</h1>
          <p className="text-muted-foreground">Shop floor operations management</p>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filter Work Orders</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search work orders..."
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
                <SelectItem value="in-progress">In Progress</SelectItem>
                <SelectItem value="paused">Paused</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="canceled">Canceled</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Work Orders Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredWorkOrders.map((order) => (
          <Card key={order._id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{order.name}</CardTitle>
                <Badge className={getStatusBadgeClass(order.status)}>
                  {order.status}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">MO: {order.manufacturingOrderId}</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Work Center: {workCenterMap.get(order.workCenterId || '') || 'N/A'}</p>
                <p className="text-sm text-muted-foreground">Duration: {order.expectedDuration} minutes</p>
              </div>
              
              <div className="flex gap-2">
                {order.status === 'In Progress' && (
                  <>
                    <Button size="sm" variant="outline" onClick={() => updateStatus({ wo_id: order._id, status: 'Paused' })} disabled={isUpdatingStatus}>
                      <Pause className="h-4 w-4 mr-1" />
                      Pause
                    </Button>
                    <Button size="sm" className="bg-success hover:bg-success/90" onClick={() => updateStatus({ wo_id: order._id, status: 'Completed' })} disabled={isUpdatingStatus}>
                      <CheckCircle className="h-4 w-4 mr-1" />
                      Complete
                    </Button>
                  </>
                )}
                {order.status === 'Paused' && (
                  <Button size="sm" className="bg-warning hover:bg-warning/90" onClick={() => updateStatus({ wo_id: order._id, status: 'In Progress' })} disabled={isUpdatingStatus}>
                    <Play className="h-4 w-4 mr-1" />
                    Resume
                  </Button>
                )}
                {order.status === 'Planned' && (
                  <Button size="sm" className="bg-primary hover:bg-primary-hover" onClick={() => updateStatus({ wo_id: order._id, status: 'In Progress' })} disabled={isUpdatingStatus}>
                    <Play className="h-4 w-4 mr-1" />
                    Start
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default WorkOrders;