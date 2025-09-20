import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Plus, Edit, Trash2, Settings } from "lucide-react";

const WorkCenters = () => {
  const [workCenters, setWorkCenters] = useState([
    { id: 1, name: "Cutting Station 1", hourlyCost: 75, status: "active" },
    { id: 2, name: "Welding Bay 2", hourlyCost: 95, status: "active" },
    { id: 3, name: "Assembly Line A", hourlyCost: 65, status: "active" },
    { id: 4, name: "Paint Floor", hourlyCost: 55, status: "maintenance" },
  ]);

  const [newCenter, setNewCenter] = useState({ name: "", hourlyCost: "" });

  const handleAddCenter = () => {
    if (newCenter.name && newCenter.hourlyCost) {
      setWorkCenters([
        ...workCenters,
        {
          id: workCenters.length + 1,
          name: newCenter.name,
          hourlyCost: parseInt(newCenter.hourlyCost),
          status: "active",
        },
      ]);
      setNewCenter({ name: "", hourlyCost: "" });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Work Centers</h1>
          <p className="text-muted-foreground">Manage production work centers and resources</p>
        </div>
        
        <Dialog>
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
                <Label htmlFor="hourlyCost">Hourly Cost ($)</Label>
                <Input
                  id="hourlyCost"
                  type="number"
                  placeholder="e.g., 75"
                  value={newCenter.hourlyCost}
                  onChange={(e) => setNewCenter({ ...newCenter, hourlyCost: e.target.value })}
                />
              </div>
              <Button onClick={handleAddCenter} className="w-full">
                Create Work Center
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {workCenters.map((center) => (
          <Card key={center.id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{center.name}</CardTitle>
                <div className="flex items-center gap-2">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    center.status === "active" 
                      ? "bg-success/10 text-success border border-success/20" 
                      : "bg-warning/10 text-warning border border-warning/20"
                  }`}>
                    {center.status}
                  </span>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Hourly Cost Rate</p>
                <p className="text-2xl font-bold">${center.hourlyCost}/hr</p>
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