import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "../components/ui/dialog";
import { toast } from "sonner";
import { Building2, Eye, EyeOff, Loader2, KeyRound, ArrowLeft } from "lucide-react";
import axios from "axios";

const API_URL = process.env.REACT_APP_BACKEND_URL;

const LoginPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  
  // Forgot Password states
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [forgotEmail, setForgotEmail] = useState("");
  const [resetStep, setResetStep] = useState(1); // 1: email, 2: new password
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await login(email, password);
      toast.success("Welcome back!");
      navigate("/dashboard");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Invalid credentials");
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setResetLoading(true);

    try {
      // Step 1: Verify email exists
      if (resetStep === 1) {
        const response = await axios.post(`${API_URL}/api/auth/verify-email`, { email: forgotEmail });
        if (response.data.exists) {
          setResetStep(2);
          toast.success("Email verified. Please set your new password.");
        }
      } 
      // Step 2: Reset password
      else if (resetStep === 2) {
        if (newPassword !== confirmPassword) {
          toast.error("Passwords do not match");
          return;
        }
        if (newPassword.length < 6) {
          toast.error("Password must be at least 6 characters");
          return;
        }
        
        await axios.post(`${API_URL}/api/auth/reset-password`, {
          email: forgotEmail,
          new_password: newPassword
        });
        
        toast.success("Password reset successfully! Please login with your new password.");
        setShowForgotPassword(false);
        setResetStep(1);
        setForgotEmail("");
        setNewPassword("");
        setConfirmPassword("");
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || "An error occurred");
    } finally {
      setResetLoading(false);
    }
  };

  const closeForgotPassword = () => {
    setShowForgotPassword(false);
    setResetStep(1);
    setForgotEmail("");
    setNewPassword("");
    setConfirmPassword("");
  };

  return (
    <div className="min-h-screen flex">
      {/* Left side - Image */}
      <div
        className="hidden lg:flex lg:w-1/2 relative bg-cover bg-center"
        style={{
          backgroundImage: `url('https://images.unsplash.com/photo-1627306036351-036986f292a9?crop=entropy&cs=srgb&fm=jpg&q=85')`,
        }}
      >
        <div className="absolute inset-0 bg-slate-900/70" />
        <div className="relative z-10 flex flex-col justify-center p-12 text-white">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center">
              <Building2 className="w-7 h-7" />
            </div>
            <div>
              <h1 className="font-heading text-2xl font-bold">RRL Builders</h1>
              <p className="text-slate-300 text-sm">Post-Sales CRM</p>
            </div>
          </div>
          <h2 className="font-heading text-4xl font-bold mb-4">
            Streamline Your Customer Management
          </h2>
          <p className="text-slate-300 text-lg leading-relaxed">
            Manage bookings, track payments, generate documents, and communicate with customers — all in one place.
          </p>
          <div className="mt-12 grid grid-cols-2 gap-6">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <p className="text-3xl font-bold text-primary">500+</p>
              <p className="text-slate-300 text-sm">Customers Managed</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <p className="text-3xl font-bold text-primary">6</p>
              <p className="text-slate-300 text-sm">Active Projects</p>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Login form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-background">
        <Card className="w-full max-w-md shadow-xl border-slate-200">
          <CardHeader className="text-center pb-2">
            <div className="lg:hidden flex justify-center mb-4">
              <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center">
                <Building2 className="w-7 h-7 text-white" />
              </div>
            </div>
            <CardTitle className="font-heading text-2xl">Welcome Back</CardTitle>
            <CardDescription>Sign in to access your CRM dashboard</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="admin@rrlbuilders.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  data-testid="login-email-input"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="pr-10"
                    data-testid="login-password-input"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              <Button
                type="submit"
                className="w-full"
                disabled={loading}
                data-testid="login-submit-btn"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  "Sign In"
                )}
              </Button>
              
              <div className="text-center">
                <button
                  type="button"
                  onClick={() => setShowForgotPassword(true)}
                  className="text-sm text-primary hover:underline"
                  data-testid="forgot-password-link"
                >
                  Forgot Password?
                </button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
      
      {/* Forgot Password Dialog */}
      <Dialog open={showForgotPassword} onOpenChange={closeForgotPassword}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <KeyRound className="w-5 h-5 text-primary" />
              {resetStep === 1 ? "Reset Password" : "Set New Password"}
            </DialogTitle>
            <DialogDescription>
              {resetStep === 1 
                ? "Enter your email address to reset your password." 
                : "Create a new password for your account."}
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleForgotPassword} className="space-y-4">
            {resetStep === 1 ? (
              <div className="space-y-2">
                <Label htmlFor="forgot-email">Email Address</Label>
                <Input
                  id="forgot-email"
                  type="email"
                  placeholder="Enter your email"
                  value={forgotEmail}
                  onChange={(e) => setForgotEmail(e.target.value)}
                  required
                  data-testid="forgot-email-input"
                />
              </div>
            ) : (
              <>
                <button
                  type="button"
                  onClick={() => setResetStep(1)}
                  className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Back
                </button>
                
                <div className="p-3 bg-slate-50 rounded-lg">
                  <p className="text-sm text-slate-600">Resetting password for:</p>
                  <p className="text-sm font-medium">{forgotEmail}</p>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="new-password">New Password</Label>
                  <div className="relative">
                    <Input
                      id="new-password"
                      type={showNewPassword ? "text" : "password"}
                      placeholder="Enter new password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      required
                      minLength={6}
                      className="pr-10"
                      data-testid="new-password-input"
                    />
                    <button
                      type="button"
                      onClick={() => setShowNewPassword(!showNewPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                    >
                      {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="confirm-password">Confirm Password</Label>
                  <Input
                    id="confirm-password"
                    type="password"
                    placeholder="Confirm new password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    minLength={6}
                    data-testid="confirm-password-input"
                  />
                </div>
              </>
            )}
            
            <div className="flex gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={closeForgotPassword}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={resetLoading}
                className="flex-1"
                data-testid="reset-password-btn"
              >
                {(() => {
                  const verifyLabel = resetStep === 1 ? "Verify Email" : "Reset Password";
                  const loadingLabel = resetStep === 1 ? "Verifying..." : "Resetting...";
                  if (resetLoading) {
                    return (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        {loadingLabel}
                      </>
                    );
                  }
                  return verifyLabel;
                })()}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default LoginPage;
