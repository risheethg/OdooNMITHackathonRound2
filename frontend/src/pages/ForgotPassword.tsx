import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Factory, Mail, ArrowLeft } from "lucide-react";

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [step, setStep] = useState<"email" | "otp" | "reset">("email");
  const [otp, setOtp] = useState("");
  const [newPassword, setNewPassword] = useState("");

  const handleSubmitEmail = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Sending OTP to:", email);
    setStep("otp");
  };

  const handleSubmitOtp = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Verifying OTP:", otp);
    setStep("reset");
  };

  const handleResetPassword = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Resetting password");
    // Would redirect to login after successful reset
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-medium">
        <CardHeader className="text-center space-y-4">
          <div className="mx-auto w-12 h-12 bg-primary rounded-lg flex items-center justify-center">
            <Factory className="h-6 w-6 text-primary-foreground" />
          </div>
          <CardTitle className="text-2xl font-bold">
            {step === "email" && "Reset Password"}
            {step === "otp" && "Enter OTP"}
            {step === "reset" && "New Password"}
          </CardTitle>
          <p className="text-muted-foreground">
            {step === "email" && "Enter your email to receive reset instructions"}
            {step === "otp" && "Enter the code sent to your email"}
            {step === "reset" && "Create your new password"}
          </p>
        </CardHeader>
        <CardContent>
          {step === "email" && (
            <form onSubmit={handleSubmitEmail} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10"
                    required
                  />
                </div>
              </div>
              <Button type="submit" className="w-full">
                Send Reset Code
              </Button>
            </form>
          )}

          {step === "otp" && (
            <form onSubmit={handleSubmitOtp} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="otp">Verification Code</Label>
                <Input
                  id="otp"
                  type="text"
                  placeholder="Enter 6-digit code"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" className="w-full">
                Verify Code
              </Button>
            </form>
          )}

          {step === "reset" && (
            <form onSubmit={handleResetPassword} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="newPassword">New Password</Label>
                <Input
                  id="newPassword"
                  type="password"
                  placeholder="Enter new password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" className="w-full">
                Reset Password
              </Button>
            </form>
          )}

          <div className="mt-4 text-center">
            <Link 
              to="/login" 
              className="inline-flex items-center text-sm text-primary hover:text-primary-hover transition-colors"
            >
              <ArrowLeft className="h-4 w-4 mr-1" />
              Back to login
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ForgotPassword;