import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Plus, Search, Edit, Trash2, FileText, Package, Settings } from "lucide-react";

const BOM = () => {
  const [searchTerm, setSearchTerm] = useState("");

  const mockBOMs = [
    {
      id: 1,
      name: "Steel Frame Assembly BOM",
      finishedProduct: "Steel Frame Assembly",
      componentCount: 8,
      operationCount: 3,
      status: "active",
    },
    {
      id: 2,
      name: "Electric Motor Unit BOM",
      finishedProduct: "Electric Motor Unit",
      componentCount: 12,
      operationCount: 5,
      status: "active",
    },
    {
      id: 3,
      name: "Control Panel Board BOM",
      finishedProduct: "Control Panel Board",
      componentCount: 15,
      operationCount: 4,
      status: "draft",
    },
  ];

  const mockComponents = [
    { name: "Steel Rod 12mm", quantity: 4, unit: "pieces" },
    { name: "Steel Plate 20mm", quantity: 2, unit: "pieces" },
    { name: "Welding Rod", quantity: 10, unit: "pieces" },
    { name: "Bolts M12", quantity: 16, unit: "pieces" },
  ];

  const mockOperations = [
    { name: "Steel Cutting", workCenter: "Cutting Station 1", duration: "2 hours" },
    { name: "Welding", workCenter: "Welding Bay 2", duration: "4 hours" },
    { name: "Quality Inspection", workCenter: "QC Station", duration: "1 hour" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Bills of Material</h1>
          <p className="text-muted-foreground">Manage product recipes and manufacturing processes</p>
        </div>
        
        <Dialog>
          <DialogTrigger asChild>
            <Button className="bg-gradient-to-r from-primary to-primary-hover">
              <Plus className="h-4 w-4 mr-2" />
              Create New BOM
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-4xl">
            <DialogHeader>
              <DialogTitle>Create New Bill of Material</DialogTitle>
            </DialogHeader>
            <div className="space-y-6">
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Finished Product</label>
                  <Input placeholder="Select or enter finished product name" />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Package className="h-5 w-5" />
                      Required Components
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {mockComponents.map((comp, index) => (
                        <div key={index} className="flex justify-between items-center p-2 bg-muted/30 rounded">
                          <span className="text-sm">{comp.name}</span>
                          <span className="text-sm font-medium">{comp.quantity} {comp.unit}</span>
                        </div>
                      ))}
                      <Button variant="outline" size="sm" className="w-full mt-2">
                        <Plus className="h-4 w-4 mr-1" />
                        Add Component
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Settings className="h-5 w-5" />
                      Manufacturing Operations
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {mockOperations.map((op, index) => (
                        <div key={index} className="p-2 bg-muted/30 rounded">
                          <div className="font-medium text-sm">{op.name}</div>
                          <div className="text-xs text-muted-foreground">
                            {op.workCenter} • {op.duration}
                          </div>
                        </div>
                      ))}
                      <Button variant="outline" size="sm" className="w-full mt-2">
                        <Plus className="h-4 w-4 mr-1" />
                        Add Operation
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              <div className="flex gap-2">
                <Button>Save as Draft</Button>
                <Button variant="outline">Activate BOM</Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Bill of Materials List</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search BOMs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mockBOMs.map((bom) => (
              <Card key={bom.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{bom.name}</CardTitle>
                    <Badge className={bom.status === "active" ? "status-completed" : "status-planned"}>
                      {bom.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">{bom.finishedProduct}</p>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Components:</span>
                    <span className="font-medium">{bom.componentCount}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Operations:</span>
                    <span className="font-medium">{bom.operationCount}</span>
                  </div>
                  
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline">
                      <FileText className="h-4 w-4 mr-1" />
                      View
                    </Button>
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
        </CardContent>
      </Card>
    </div>
  );
};

export default BOM;