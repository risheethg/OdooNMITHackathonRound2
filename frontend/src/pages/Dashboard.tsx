import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, Search, Filter, Edit, Trash2, Eye, Circle } from "lucide-react";
import { KPICard } from "@/components/dashboard/KPICard";
import { OrdersTable } from "@/components/dashboard/OrdersTable";

const Dashboard = () => {
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");

  const kpiData = [
    {
      title: "Orders Completed",
      value: "24",
      change: "+12%",
      trend: "up" as const,
      color: "success" as const,
    },
    {
      title: "In Progress",
      value: "8",
      change: "-2",
      trend: "down" as const,
      color: "warning" as const,
    },
    {
      title: "Delayed",
      value: "3",
      change: "+1",
      trend: "up" as const,
      color: "destructive" as const,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Manufacturing Orders</h1>
          <p className="text-muted-foreground">Manage and track all manufacturing orders</p>
        </div>
        <Button className="bg-gradient-to-r from-primary to-primary-hover">
          <Plus className="h-4 w-4 mr-2" />
          Create New Order
        </Button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {kpiData.map((kpi, index) => (
          <KPICard key={index} {...kpi} />
        ))}
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle>Order Management</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search orders..."
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

          {/* Orders Table */}
          <OrdersTable searchTerm={searchTerm} statusFilter={statusFilter} />
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;