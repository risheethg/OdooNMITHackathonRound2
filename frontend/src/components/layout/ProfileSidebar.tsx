import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { User, FileText, Settings, LogOut, X } from "lucide-react";
import { useAuth } from "@/Root";

interface ProfileSidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const ProfileSidebar = ({ isOpen, onClose }: ProfileSidebarProps) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleSignOut = () => {
    logout();
    onClose();
  };

  // Get user initials for avatar fallback
  const getUserInitials = (email: string) => {
    return email.split('@')[0].charAt(0).toUpperCase();
  };

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent side="left" className="w-80 p-0">
        <SheetHeader className="p-6 border-b">
          <div className="flex items-center justify-between">
            <SheetTitle>Profile & Settings</SheetTitle>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </SheetHeader>
        
        <div className="p-6">
          {/* User Profile Section */}
          {user && (
            <div className="flex items-center gap-4 mb-6">
              <Avatar className="h-16 w-16">
                <AvatarImage src="/placeholder-avatar.jpg" alt="User" />
                <AvatarFallback className="text-lg">
                  {getUserInitials(user.email)}
                </AvatarFallback>
              </Avatar>
              <div>
                <h3 className="font-semibold text-lg">{user.email.split('@')[0]}</h3>
                <p className="text-muted-foreground">{user.role}</p>
                <p className="text-sm text-muted-foreground">{user.email}</p>
              </div>
            </div>
          )}

          {/* Navigation Links */}
          <nav className="space-y-2">
            <Link to="/profile" onClick={onClose}>
              <Button variant="ghost" className="w-full justify-start">
                <User className="h-4 w-4 mr-3" />
                My Profile
              </Button>
            </Link>
            
            <Link to="/reports" onClick={onClose}>
              <Button variant="ghost" className="w-full justify-start">
                <FileText className="h-4 w-4 mr-3" />
                My Reports
              </Button>
            </Link>
            
            <Link to="/settings" onClick={onClose}>
              <Button variant="ghost" className="w-full justify-start">
                <Settings className="h-4 w-4 mr-3" />
                Settings
              </Button>
            </Link>
          </nav>

          {/* Logout Button */}
          <div className="mt-8 pt-4 border-t">
            <Button 
              variant="outline" 
              className="w-full justify-start text-destructive hover:text-destructive"
              onClick={handleSignOut}
            >
              <LogOut className="h-4 w-4 mr-3" />
              Sign Out
            </Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
};

export { ProfileSidebar };