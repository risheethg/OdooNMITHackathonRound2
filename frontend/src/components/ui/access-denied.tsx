import { AlertTriangle } from "lucide-react";

interface AccessDeniedProps {
  resource?: string;
  message?: string;
}

export function AccessDenied({ 
  resource = "this resource", 
  message = "Contact your administrator if you believe this is an error." 
}: AccessDeniedProps) {
  return (
    <div className="text-center p-8 max-w-md mx-auto">
      <div className="mx-auto w-16 h-16 mb-4 text-red-500">
        <AlertTriangle className="w-full h-full" />
      </div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
      <p className="text-gray-600 mb-4">
        You don't have permission to access {resource}.
      </p>
      <p className="text-sm text-gray-500">{message}</p>
    </div>
  );
}