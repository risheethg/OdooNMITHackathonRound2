import { Card, CardContent } from "@/components/ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface KPICardProps {
  title: string;
  value: string;
  change: string;
  trend: "up" | "down";
  color: "success" | "warning" | "destructive";
}

const KPICard = ({ title, value, change, trend, color }: KPICardProps) => {
  const colorClasses = {
    success: "border-success/20 bg-success/5",
    warning: "border-warning/20 bg-warning/5",
    destructive: "border-destructive/20 bg-destructive/5",
  };

  const textColorClasses = {
    success: "text-success",
    warning: "text-warning",
    destructive: "text-destructive",
  };

  return (
    <Card className={cn("kpi-card transition-all hover:scale-105", colorClasses[color])}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground mb-1">{title}</p>
            <p className="text-3xl font-bold">{value}</p>
          </div>
          <div className={cn("flex items-center gap-1 text-sm font-medium", textColorClasses[color])}>
            {trend === "up" ? (
              <TrendingUp className="h-4 w-4" />
            ) : (
              <TrendingDown className="h-4 w-4" />
            )}
            {change}
          </div>
        </div>
        <div className="mt-4">
          <div className={cn("h-2 rounded-full", colorClasses[color])}>
            <div 
              className={cn("h-full rounded-full transition-all", 
                color === "success" ? "bg-success" : 
                color === "warning" ? "bg-warning" : "bg-destructive"
              )}
              style={{ width: `${Math.abs(parseInt(change))}%` }}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export { KPICard };