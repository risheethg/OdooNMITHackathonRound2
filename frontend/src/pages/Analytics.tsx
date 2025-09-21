import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { BarChart3, TrendingUp, TrendingDown, Download, Calendar, Timer, CheckSquare, XSquare, Hourglass } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/Root";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// --- API SERVICE AND TYPES ---
const API_URL = "http://127.0.0.1:8000";

interface ApiResponse<T> {
  data: T;
  message: string;
  status_code: number;
}

interface StatusOverview {
  planned: number;
  in_progress: number;
  done: number;
  cancelled: number;
}

interface ThroughputDataPoint {
  date: string;
  count: number;
}

interface ProductionThroughput {
  period: string;
  data: ThroughputDataPoint[];
}

interface AverageCycleTime {
  average_hours: number;
  average_minutes: number;
  total_orders_calculated: number;
}

const getStatusOverview = async (token: string): Promise<StatusOverview> => {
  const res = await fetch(`${API_URL}/analytics/overview`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error("Failed to fetch status overview");
  const result: ApiResponse<StatusOverview> = await res.json();
  return result.data;
};

const getProductionThroughput = async (days: number, token: string): Promise<ProductionThroughput> => {
  const res = await fetch(`${API_URL}/analytics/throughput?period_days=${days}`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error("Failed to fetch production throughput");
  const result: ApiResponse<ProductionThroughput> = await res.json();
  return result.data;
};

const getAverageCycleTime = async (token: string): Promise<AverageCycleTime> => {
  const res = await fetch(`${API_URL}/analytics/cycle-time`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error("Failed to fetch average cycle time");
  const result: ApiResponse<AverageCycleTime> = await res.json();
  return result.data;
};

const Analytics = () => {
  const [timePeriod, setTimePeriod] = useState(30);
  const { idToken } = useAuth();

  const { data: overview, isLoading: isLoadingOverview } = useQuery<StatusOverview, Error>({
    queryKey: ['analyticsOverview'],
    queryFn: () => getStatusOverview(idToken!),
    enabled: !!idToken,
  });

  const { data: throughput, isLoading: isLoadingThroughput } = useQuery<ProductionThroughput, Error>({
    queryKey: ['productionThroughput', timePeriod],
    queryFn: () => getProductionThroughput(timePeriod, idToken!),
    enabled: !!idToken,
  });

  const { data: cycleTime, isLoading: isLoadingCycleTime } = useQuery<AverageCycleTime, Error>({
    queryKey: ['averageCycleTime'],
    queryFn: () => getAverageCycleTime(idToken!),
    enabled: !!idToken,
  });

  const kpiMetrics = useMemo(() => {
    const totalOrders = (overview?.planned || 0) + (overview?.in_progress || 0) + (overview?.done || 0) + (overview?.cancelled || 0);
    return [
      {
        title: "Avg. Cycle Time",
        value: isLoadingCycleTime ? "..." : `${cycleTime?.average_hours.toFixed(1) || 0} hrs`,
        description: `Calculated from ${cycleTime?.total_orders_calculated || 0} orders`,
        icon: Timer,
      },
      {
        title: "Orders Completed",
        value: isLoadingOverview ? "..." : overview?.done.toString() || "0",
        description: `Out of ${totalOrders} total orders`,
        icon: CheckSquare,
      },
      {
        title: "In Progress",
        value: isLoadingOverview ? "..." : overview?.in_progress.toString() || "0",
        description: "Currently on the shop floor",
        icon: Hourglass,
      },
      {
        title: "Orders Cancelled",
        value: isLoadingOverview ? "..." : overview?.cancelled.toString() || "0",
        description: "Orders that were stopped",
        icon: XSquare,
      },
    ];
  }, [overview, cycleTime, isLoadingOverview, isLoadingCycleTime]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
          <p className="text-muted-foreground">Production performance insights and metrics</p>
        </div>
        
        <div className="flex gap-2">
          <Select defaultValue={timePeriod.toString()} onValueChange={(val) => setTimePeriod(parseInt(val))}>
            <SelectTrigger className="w-40">
              <Calendar className="h-4 w-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
          
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* KPI Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpiMetrics.map((metric, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{metric.title}</CardTitle>
              <metric.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="space-y-1">
                <p className="text-3xl font-bold">{metric.value}</p>
                <p className="text-xs text-muted-foreground">{metric.description}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6">
        {/* Production Chart Placeholder */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Production Throughput
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoadingThroughput ? (
              <div className="h-80 flex items-center justify-center text-muted-foreground">Loading chart data...</div>
            ) : (
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={throughput?.data}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} name="Completed Orders" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Analytics;