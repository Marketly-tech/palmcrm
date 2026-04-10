import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription,
} from "../ui/dialog";
import { KeyRound, Loader2, Eye, EyeOff } from "lucide-react";

const ResetPasswordDialog = ({
  open, onOpenChange, resetPasswordUser,
  newPassword, setNewPassword, confirmPassword, setConfirmPassword,
  showNewPassword, setShowNewPassword, resettingPassword, onReset,
}) => (
  <Dialog open={open} onOpenChange={onOpenChange}>
    <DialogContent className="sm:max-w-md">
      <DialogHeader>
        <DialogTitle className="flex items-center gap-2">
          <KeyRound className="w-5 h-5 text-primary" />
          Reset Password
        </DialogTitle>
        <DialogDescription>Set a new password for this user</DialogDescription>
      </DialogHeader>
      {resetPasswordUser && (
        <div className="space-y-4">
          <div className="p-3 bg-slate-50 rounded-lg">
            <p className="text-sm text-slate-600">Resetting password for:</p>
            <p className="font-medium">{resetPasswordUser.name}</p>
            <p className="text-sm text-slate-500">{resetPasswordUser.email}</p>
          </div>
          <div className="space-y-2">
            <Label>New Password</Label>
            <div className="relative">
              <Input
                type={showNewPassword ? "text" : "password"}
                value={newPassword} onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Minimum 6 characters" className="pr-10"
                data-testid="admin-new-password"
              />
              <button type="button" onClick={() => setShowNewPassword(!showNewPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>
          <div className="space-y-2">
            <Label>Confirm Password</Label>
            <Input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} placeholder="Re-enter new password" data-testid="admin-confirm-password" />
          </div>
          <div className="flex gap-2 pt-4">
            <Button variant="outline" onClick={() => onOpenChange(false)} className="flex-1">Cancel</Button>
            <Button onClick={onReset} disabled={resettingPassword || !newPassword || !confirmPassword} className="flex-1" data-testid="admin-reset-password-btn">
              {resettingPassword ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
              Reset Password
            </Button>
          </div>
        </div>
      )}
    </DialogContent>
  </Dialog>
);

export default ResetPasswordDialog;
