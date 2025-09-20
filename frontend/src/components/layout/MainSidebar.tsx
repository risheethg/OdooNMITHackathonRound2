import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  Factory,
  ClipboardList,
  Settings,
  Package,
  FileText,
  BarChart3,
} from "lucide-react";

const navigation = [
  {
    name: "Manufacturing Orders",
    href: "/dashboard",
    icon: Factory,
    description: "Dashboard",
  },
  {
    name: "Work Orders",
    href: "/work-orders",
    icon: ClipboardList,
    description: "Shop Floor Operations",
  },
  {
    name: "Work Centers",
    href: "/work-centers",
    icon: Settings,
    description: "Resource Management",
  },
  {
    name: "Stock Ledger",
    href: "/stock-ledger",
    icon: Package,
    description: "Inventory Tracking",
  },
  {
    name: "Bills of Material",
    href: "/bom",
    icon: FileText,
    description: "Product Recipes",
  },
  {
    name: "Analytics",
    href: "/analytics",
    icon: BarChart3,
    description: "Performance Insights",
  },
];

const MainSidebar = () => {
  const location = useLocation();

  return (
    <aside className="w-64 bg-card border-r border-border flex flex-col">
      {/* Sidebar Header */}
      <div className="p-6 border-b border-border">
        <h2 className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
          Master Menu
        </h2>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href;
          
          return (
            <Link key={item.name} to={item.href}>
              <Button
                variant="ghost"
                className={cn(
                  "w-full justify-start h-auto p-3 text-left",
                  isActive && "bg-primary/10 text-primary hover:bg-primary/15"
                )}
              >
                <item.icon className="h-5 w-5 mr-3 flex-shrink-0" />
                <div className="flex flex-col items-start">
                  <span className="font-medium text-sm">{item.name}</span>
                  <span className="text-xs text-muted-foreground">
                    {item.description}
                  </span>
                </div>
              </Button>
            </Link>
          );
        })}
      </nav>

      {/* Sidebar Footer */}
      <div className="p-4 border-t border-border">
        <div className="text-xs text-muted-foreground">
          Manufacturing System v2.1
        </div>
      </div>
    </aside>
  );
};

export { MainSidebar };