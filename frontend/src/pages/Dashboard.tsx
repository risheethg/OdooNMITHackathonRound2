import { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Plus, Search, Filter } from "lucide-react";
import { KPICard } from "@/components/dashboard/KPICard";
import { OrdersTable } from "@/components/dashboard/OrdersTable";
import { useQuery } from "@tanstack/react-query";
import { getManufacturingOrders, ManufacturingOrder } from "@/services/manufacturingOrders";
import { useAuth } from "@/Root";

const Dashboard = () => {
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const { idToken } = useAuth();

  // A single query for all data, which will be filtered on the client for KPIs
  const { data: allOrders = [], isLoading: isLoadingKpis } = useQuery<ManufacturingOrder[], Error>({
    queryKey: ['manufacturingOrders', 'all', ''], // Fetch all for KPIs
    queryFn: () => getManufacturingOrders('all', '', idToken!),
    enabled: !!idToken,
  });

  const kpiData = useMemo(() => {
    if (isLoadingKpis) return [];
    const completed = allOrders.filter(o => o.status === 'completed').length;
    const inProgress = allOrders.filter(o => o.status === 'progress').length;
    const delayed = allOrders.filter(o => o.status === 'delayed').length;

    return [
      {
        title: "Orders Completed",
        value: completed.toString(),
        change: "", // You might calculate this based on a previous period
        trend: "up" as const,
        color: "success" as const,
      },
      {
        title: "In Progress",
        value: inProgress.toString(),
        change: "",
        trend: "up" as const,
        color: "warning" as const,
      },
      {
        title: "Delayed",
        value: delayed.toString(),
        change: "",
        trend: "up" as const,
        color: "destructive" as const,
      },
    ];
  }, [allOrders, isLoadingKpis]);

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
          <CardDescription>View, search, and filter all manufacturing orders.</CardDescription>
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