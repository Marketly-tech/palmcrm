import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription,
} from "../ui/dialog";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "../ui/select";
import { Edit, Loader2 } from "lucide-react";

const EditUserDialog = ({ open, onOpenChange, editingUser, setEditingUser, saving, onSave, getRoleDescription }) => (
  <Dialog open={open} onOpenChange={onOpenChange}>
    <DialogContent className="sm:max-w-md">
      <DialogHeader>
        <DialogTitle className="flex items-center gap-2">
          <Edit className="w-5 h-5 text-primary" />
          Edit User
        </DialogTitle>
        <DialogDescription>Update user details and permissions</DialogDescription>
      </DialogHeader>
      {editingUser && (
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Full Name</Label>
            <Input value={editingUser.name} onChange={(e) => setEditingUser({ ...editingUser, name: e.target.value })} data-testid="edit-user-name" />
          </div>
          <div className="space-y-2">
            <Label>Email</Label>
            <Input value={editingUser.email} disabled className="bg-slate-50" />
            <p className="text-xs text-slate-500">Email cannot be changed</p>
          </div>
          <div className="space-y-2">
            <Label>Phone</Label>
            <Input value={editingUser.phone || ""} onChange={(e) => setEditingUser({ ...editingUser, phone: e.target.value })} placeholder="9876543210" data-testid="edit-user-phone" />
          </div>
          <div className="space-y-2">
            <Label>Role</Label>
            <Select value={editingUser.role} onValueChange={(value) => setEditingUser({ ...editingUser, role: value })}>
              <SelectTrigger data-testid="edit-user-role"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="admin">Admin</SelectItem>
                <SelectItem value="manager">Manager</SelectItem>
                <SelectItem value="accounts">Accounts</SelectItem>
                <SelectItem value="sales">Sales</SelectItem>
                <SelectItem value="support">Support</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-slate-500">{getRoleDescription(editingUser.role)}</p>
          </div>
          <div className="space-y-2">
            <Label>Status</Label>
            <Select value={editingUser.is_active ? "active" : "inactive"} onValueChange={(value) => setEditingUser({ ...editingUser, is_active: value === "active" })}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex gap-2 pt-4">
            <Button variant="outline" onClick={() => onOpenChange(false)} className="flex-1">Cancel</Button>
            <Button onClick={onSave} disabled={saving} className="flex-1" data-testid="save-edit-user-btn">
              {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
              Save Changes
            </Button>
          </div>
        </div>
      )}
    </DialogContent>
  </Dialog>
);

export default EditUserDialog;
