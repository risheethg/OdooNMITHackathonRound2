import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Plus, Edit, Trash2, Settings } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useAuth } from "@/Root";

const API_URL = "http://127.0.0.1:8000";

interface WorkCenter {
  _id: string;
  name: string;
  operation?: string;
  cost_per_hour?: number;
  created_at: string;
  updated_at: string;
}

interface WorkCenterCreate {
  name: string;
  operation?: string;
  cost_per_hour?: number;
}

// API functions
const getWorkCenters = async (token: string): Promise<WorkCenter[]> => {
  const response = await fetch(`${API_URL}/api/work-centres/`, { 
    headers: { Authorization: `Bearer ${token}` } 
  });
  if (!response.ok) throw new Error('Failed to fetch work centers');
  const result = await response.json();
  return result.data;
};

const createWorkCenter = async (data: WorkCenterCreate, token: string): Promise<WorkCenter> => {
  const response = await fetch(`${API_URL}/api/work-centres/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.message || 'Failed to create work center');
  }
  const result = await response.json();
  return result.data;
};

const WorkCenters = () => {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newCenter, setNewCenter] = useState({ 
    name: "", 
    operation: "", 
    cost_per_hour: "" 
  });

  const { data: workCenters = [], isLoading, error } = useQuery<WorkCenter[], Error>({
    queryKey: ['workCenters'],
    queryFn: () => getWorkCenters(token!),
    enabled: !!token,
  });

  const { mutate: createWorkCenterMutation, isPending: isCreating } = useMutation({
    mutationFn: (data: WorkCenterCreate) => createWorkCenter(data, token!),
    onSuccess: () => {
      toast.success('Work center created successfully!');
      queryClient.invalidateQueries({ queryKey: ['workCenters'] });
      setNewCenter({ name: "", operation: "", cost_per_hour: "" });
      setDialogOpen(false);
    },
    onError: (error) => {
      toast.error(`Error: ${error.message}`);
    },
  });

  const handleAddCenter = () => {
    if (newCenter.name.trim()) {
      const data: WorkCenterCreate = {
        name: newCenter.name.trim(),
        operation: newCenter.operation.trim() || undefined,
        cost_per_hour: newCenter.cost_per_hour ? parseFloat(newCenter.cost_per_hour) : undefined,
      };
      createWorkCenterMutation(data);
    }
  };

  if (isLoading) return <div>Loading work centers...</div>;
  if (error) return <div>Error loading work centers: {error.message}</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Work Centers</h1>
          <p className="text-muted-foreground">Manage production work centers and resources</p>
        </div>
        
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-gradient-to-r from-primary to-primary-hover">
              <Plus className="h-4 w-4 mr-2" />
              Add Work Center
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Work Center</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="centerName">Work Center Name</Label>
                <Input
                  id="centerName"
                  placeholder="e.g., Assembly Line B"
                  value={newCenter.name}
                  onChange={(e) => setNewCenter({ ...newCenter, name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="operation">Operation</Label>
                <Input
                  id="operation"
                  placeholder="e.g., Assembly, Cutting, Welding"
                  value={newCenter.operation}
                  onChange={(e) => setNewCenter({ ...newCenter, operation: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="costPerHour">Cost Per Hour ($)</Label>
                <Input
                  id="costPerHour"
                  type="number"
                  placeholder="e.g., 75"
                  value={newCenter.cost_per_hour}
                  onChange={(e) => setNewCenter({ ...newCenter, cost_per_hour: e.target.value })}
                />
              </div>
              <Button 
                onClick={handleAddCenter} 
                className="w-full"
                disabled={isCreating || !newCenter.name.trim()}
              >
                {isCreating ? 'Creating...' : 'Create Work Center'}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {workCenters.map((center) => (
          <Card key={center._id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{center.name}</CardTitle>
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-success/10 text-success border border-success/20">
                    Active
                  </span>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {center.operation && (
                <div>
                  <p className="text-sm text-muted-foreground">Operation</p>
                  <p className="font-medium">{center.operation}</p>
                </div>
              )}
              <div>
                <p className="text-sm text-muted-foreground">Cost Per Hour</p>
                <p className="text-2xl font-bold">
                  {center.cost_per_hour ? `$${center.cost_per_hour}/hr` : 'Not set'}
                </p>
              </div>
              
              <div className="flex gap-2">
                <Button size="sm" variant="outline">
                  <Edit className="h-4 w-4 mr-1" />
                  Edit
                </Button>
                <Button size="sm" variant="outline" className="text-destructive hover:text-destructive">
                  <Trash2 className="h-4 w-4 mr-1" />
                  Delete
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default WorkCenters;