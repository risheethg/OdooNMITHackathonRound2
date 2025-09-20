import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { ClipboardList, Play, Pause, CheckCircle, Search, Filter } from "lucide-react";
import { useState } from "react";

const WorkOrders = () => {
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");

  const mockWorkOrders = [
    {
      id: "WO-001",
      manufacturingOrderId: "MO-2024-001",
      operation: "Steel Cutting",
      workCenter: "Cutting Station 1",
      assignee: "John Smith",
      status: "started",
      estimatedDuration: "4 hours",
    },
    {
      id: "WO-002",
      manufacturingOrderId: "MO-2024-001",
      operation: "Welding",
      workCenter: "Welding Bay 2",
      assignee: "Sarah Johnson",
      status: "paused",
      estimatedDuration: "6 hours",
    },
    {
      id: "WO-003",
      manufacturingOrderId: "MO-2024-002",
      operation: "Assembly",
      workCenter: "Assembly Line A",
      assignee: "Mike Wilson",
      status: "completed",
      estimatedDuration: "8 hours",
    },
  ];

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
                <SelectItem value="started">Started</SelectItem>
                <SelectItem value="paused">Paused</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Work Orders Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockWorkOrders.map((order) => (
          <Card key={order.id} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{order.id}</CardTitle>
                <Badge className={
                  order.status === "started" ? "status-progress" :
                  order.status === "paused" ? "status-planned" :
                  "status-completed"
                }>
                  {order.status}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">MO: {order.manufacturingOrderId}</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="font-medium">{order.operation}</p>
                <p className="text-sm text-muted-foreground">{order.workCenter}</p>
                <p className="text-sm text-muted-foreground">Assignee: {order.assignee}</p>
                <p className="text-sm text-muted-foreground">Duration: {order.estimatedDuration}</p>
              </div>
              
              <div className="flex gap-2">
                {order.status === "started" && (
                  <>
                    <Button size="sm" variant="outline">
                      <Pause className="h-4 w-4 mr-1" />
                      Pause
                    </Button>
                    <Button size="sm" className="bg-success hover:bg-success/90">
                      <CheckCircle className="h-4 w-4 mr-1" />
                      Complete
                    </Button>
                  </>
                )}
                {order.status === "paused" && (
                  <Button size="sm" className="bg-warning hover:bg-warning/90">
                    <Play className="h-4 w-4 mr-1" />
                    Resume
                  </Button>
                )}
                {order.status !== "completed" && order.status !== "started" && (
                  <Button size="sm" className="bg-primary hover:bg-primary-hover">
                    <Play className="h-4 w-4 mr-1" />
                    Start Timer
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