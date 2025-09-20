import { useState } from "react";
import { Outlet } from "react-router-dom";
import { ProfileSidebar } from "./ProfileSidebar";
import { MainSidebar } from "./MainSidebar";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Factory, User } from "lucide-react";

const AppLayout = () => {
  const [isProfileSidebarOpen, setIsProfileSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background flex">
      {/* Profile Sidebar */}
      <ProfileSidebar 
        isOpen={isProfileSidebarOpen} 
        onClose={() => setIsProfileSidebarOpen(false)} 
      />

      {/* Main Sidebar */}
      <MainSidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Header */}
        <header className="h-16 border-b border-border bg-card/50 backdrop-blur-sm flex items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <Factory className="h-6 w-6 text-primary" />
            <h1 className="text-lg font-semibold">Manufacturing Management</h1>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsProfileSidebarOpen(true)}
            className="flex items-center gap-2"
          >
            <Avatar className="h-8 w-8">
              <AvatarImage src="/placeholder-avatar.jpg" alt="User" />
              <AvatarFallback>
                <User className="h-4 w-4" />
              </AvatarFallback>
            </Avatar>
            <span className="text-sm font-medium">John Doe</span>
          </Button>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AppLayout;