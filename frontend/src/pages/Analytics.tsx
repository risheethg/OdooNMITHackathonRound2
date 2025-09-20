import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { BarChart3, TrendingUp, TrendingDown, Activity, Download, Calendar } from "lucide-react";

const Analytics = () => {
  const kpiMetrics = [
    {
      title: "Production Throughput",
      value: "94.2%",
      change: "+5.2%",
      trend: "up",
      description: "Average efficiency this month",
    },
    {
      title: "Order Delays",
      value: "8.5%",
      change: "-2.1%",
      trend: "down",
      description: "Percentage of delayed orders",
    },
    {
      title: "Resource Utilization",
      value: "87.3%",
      change: "+3.8%",
      trend: "up",
      description: "Average work center usage",
    },
    {
      title: "Quality Rate",
      value: "98.1%",
      change: "+0.5%",
      trend: "up",
      description: "First-pass quality rate",
    },
  ];

  const recentAlerts = [
    {
      type: "warning",
      message: "Work Center 3 approaching capacity limit",
      time: "2 hours ago",
    },
    {
      type: "info",
      message: "Monthly production target achieved",
      time: "5 hours ago",
    },
    {
      type: "error",
      message: "Material shortage detected for Steel Rod 12mm",
      time: "1 day ago",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
          <p className="text-muted-foreground">Production performance insights and metrics</p>
        </div>
        
        <div className="flex gap-2">
          <Select defaultValue="30d">
            <SelectTrigger className="w-40">
              <Calendar className="h-4 w-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 3 months</SelectItem>
              <SelectItem value="1y">Last year</SelectItem>
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
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-muted-foreground">{metric.title}</h3>
                {metric.trend === "up" ? (
                  <TrendingUp className="h-4 w-4 text-success" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-destructive" />
                )}
              </div>
              <div className="space-y-1">
                <p className="text-3xl font-bold">{metric.value}</p>
                <div className="flex items-center gap-1">
                  <span className={`text-sm font-medium ${
                    metric.trend === "up" ? "text-success" : "text-destructive"
                  }`}>
                    {metric.change}
                  </span>
                  <span className="text-sm text-muted-foreground">vs last period</span>
                </div>
                <p className="text-xs text-muted-foreground">{metric.description}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Production Chart Placeholder */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Production Trends
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 bg-muted/30 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <BarChart3 className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-muted-foreground">Production chart would go here</p>
                <p className="text-sm text-muted-foreground">Interactive charts showing daily/weekly production data</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Resource Utilization */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Work Center Utilization
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { name: "Cutting Station 1", utilization: 92 },
                { name: "Welding Bay 2", utilization: 87 },
                { name: "Assembly Line A", utilization: 78 },
                { name: "Paint Floor", utilization: 65 },
              ].map((center, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">{center.name}</span>
                    <span className="text-sm font-medium">{center.utilization}%</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all ${
                        center.utilization > 85 ? "bg-warning" :
                        center.utilization > 70 ? "bg-success" : "bg-primary"
                      }`}
                      style={{ width: `${center.utilization}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Alerts and Notifications */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Alerts & Notifications</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {recentAlerts.map((alert, index) => (
              <div key={index} className="flex items-center gap-3 p-3 rounded-lg border">
                <Badge className={
                  alert.type === "warning" ? "status-progress" :
                  alert.type === "error" ? "status-delayed" : "status-completed"
                }>
                  {alert.type}
                </Badge>
                <div className="flex-1">
                  <p className="text-sm">{alert.message}</p>
                </div>
                <span className="text-xs text-muted-foreground">{alert.time}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Analytics;