import { useState, useEffect } from "react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogDescription,
} from "../components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { toast } from "sonner";
import {
  Users,
  Settings,
  Plus,
  Loader2,
  Shield,
  UserPlus,
  Trash2,
  Edit,
  KeyRound,
  Eye,
  EyeOff,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SettingsPage = () => {
  const { user, hasRole } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userDialogOpen, setUserDialogOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  // Edit user state
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  
  // Reset password state
  const [resetPasswordDialogOpen, setResetPasswordDialogOpen] = useState(false);
  const [resetPasswordUser, setResetPasswordUser] = useState(null);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [resettingPassword, setResettingPassword] = useState(false);

  const [newUser, setNewUser] = useState({
    name: "",
    email: "",
    password: "",
    role: "sales",
    phone: "",
  });

  useEffect(() => {
    if (hasRole("admin")) {
      fetchUsers();
    } else {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- fetchUsers is stable, runs once on mount
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      setUsers(response.data);
    } catch (error) {
      toast.error("Failed to fetch users");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async () => {
    if (!newUser.name || !newUser.email || !newUser.password) {
      toast.error("Please fill all required fields");
      return;
    }

    setSaving(true);
    try {
      await axios.post(`${API}/auth/register`, newUser);
      fetchUsers();
      setUserDialogOpen(false);
      setNewUser({ name: "", email: "", password: "", role: "sales", phone: "" });
      toast.success("User created successfully");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to create user");
    } finally {
      setSaving(false);
    }
  };

  const handleEditUser = (userToEdit) => {
    setEditingUser({ ...userToEdit });
    setEditDialogOpen(true);
  };

  const handleSaveUserEdit = async () => {
    if (!editingUser) return;
    
    setSaving(true);
    try {
      await axios.put(`${API}/users/${editingUser.id}`, {
        name: editingUser.name,
        role: editingUser.role,
        phone: editingUser.phone,
        is_active: editingUser.is_active,
      });
      fetchUsers();
      setEditDialogOpen(false);
      setEditingUser(null);
      toast.success("User updated successfully");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to update user");
    } finally {
      setSaving(false);
    }
  };

  const handleOpenResetPassword = (userToReset) => {
    setResetPasswordUser(userToReset);
    setNewPassword("");
    setConfirmPassword("");
    setShowNewPassword(false);
    setResetPasswordDialogOpen(true);
  };

  const handleResetPassword = async () => {
    if (!resetPasswordUser) return;
    
    if (newPassword.length < 6) {
      toast.error("Password must be at least 6 characters");
      return;
    }
    
    if (newPassword !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }
    
    setResettingPassword(true);
    try {
      await axios.post(`${API}/admin/reset-user-password`, {
        user_id: resetPasswordUser.id,
        new_password: newPassword,
      });
      setResetPasswordDialogOpen(false);
      setResetPasswordUser(null);
      setNewPassword("");
      setConfirmPassword("");
      toast.success(`Password reset successfully for ${resetPasswordUser.name}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to reset password");
    } finally {
      setResettingPassword(false);
    }
  };

  const handleToggleUserStatus = async (userId, isActive) => {
    try {
      await axios.put(`${API}/users/${userId}`, { is_active: !isActive });
      fetchUsers();
      toast.success(`User ${isActive ? "deactivated" : "activated"}`);
    } catch (error) {
      toast.error("Failed to update user");
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm("Are you sure you want to delete this user?")) return;
    
    try {
      await axios.delete(`${API}/users/${userId}`);
      fetchUsers();
      toast.success("User deleted");
    } catch (error) {
      toast.error("Failed to delete user");
    }
  };

  const getRoleBadge = (role) => {
    const styles = {
      admin: "bg-red-100 text-red-700",
      manager: "bg-purple-100 text-purple-700",
      accounts: "bg-blue-100 text-blue-700",
      sales: "bg-green-100 text-green-700",
      support: "bg-yellow-100 text-yellow-700",
    };
    return styles[role] || "bg-slate-100 text-slate-700";
  };

  const getRoleDescription = (role) => {
    const descriptions = {
      admin: "Full access to all features including user management",
      manager: "Can manage customers, leads, and view reports",
      accounts: "Can manage payments and financial documents",
      sales: "Can view and update customer information",
      support: "Limited access to customer support features",
    };
    return descriptions[role] || "Standard user access";
  };

  return (
    <div className="space-y-6" data-testid="settings-page">
      {/* Header */}
      <div>
        <h1 className="font-heading text-3xl font-bold text-slate-900">Settings</h1>
        <p className="text-slate-500 mt-1">Manage users and system settings</p>
      </div>

      <Tabs defaultValue="users" className="space-y-4">
        <TabsList>
          <TabsTrigger value="users" data-testid="tab-users">
            <Users className="w-4 h-4 mr-2" />
            User Management
          </TabsTrigger>
          <TabsTrigger value="general" data-testid="tab-general">
            <Settings className="w-4 h-4 mr-2" />
            General
          </TabsTrigger>
        </TabsList>

        {/* Users Tab */}
        <TabsContent value="users">
          {hasRole("admin") ? (
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>User Management</CardTitle>
                  <CardDescription>Manage CRM users and their roles</CardDescription>
                </div>
                <Dialog open={userDialogOpen} onOpenChange={setUserDialogOpen}>
                  <DialogTrigger asChild>
                    <Button data-testid="add-user-btn">
                      <UserPlus className="w-4 h-4 mr-2" />
                      Add User
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Create New User</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label>Full Name *</Label>
                        <Input
                          value={newUser.name}
                          onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                          placeholder="John Doe"
                          data-testid="user-name-input"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Email *</Label>
                        <Input
                          type="email"
                          value={newUser.email}
                          onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                          placeholder="john@rrlbuilders.com"
                          data-testid="user-email-input"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Password *</Label>
                        <Input
                          type="password"
                          value={newUser.password}
                          onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                          placeholder="Minimum 6 characters"
                          data-testid="user-password-input"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Phone</Label>
                        <Input
                          value={newUser.phone}
                          onChange={(e) => setNewUser({ ...newUser, phone: e.target.value })}
                          placeholder="9876543210"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Role</Label>
                        <Select
                          value={newUser.role}
                          onValueChange={(value) => setNewUser({ ...newUser, role: value })}
                        >
                          <SelectTrigger data-testid="user-role-select">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="admin">Admin</SelectItem>
                            <SelectItem value="manager">Manager</SelectItem>
                            <SelectItem value="accounts">Accounts</SelectItem>
                            <SelectItem value="sales">Sales</SelectItem>
                            <SelectItem value="support">Support</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <Button
                        onClick={handleCreateUser}
                        className="w-full"
                        disabled={saving}
                        data-testid="save-user-btn"
                      >
                        {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                        Create User
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="flex items-center justify-center h-32">
                    <Loader2 className="w-8 h-8 animate-spin text-primary" />
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Email</TableHead>
                        <TableHead>Role</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {users.map((u) => (
                        <TableRow key={u.id}>
                          <TableCell className="font-medium">{u.name}</TableCell>
                          <TableCell>{u.email}</TableCell>
                          <TableCell>
                            <Badge className={getRoleBadge(u.role)}>{u.role}</Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant={u.is_active ? "default" : "secondary"}>
                              {u.is_active ? "Active" : "Inactive"}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex gap-2 justify-end">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleEditUser(u)}
                                title="Edit User"
                                data-testid={`edit-user-${u.id}`}
                              >
                                <Edit className="w-4 h-4" />
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleOpenResetPassword(u)}
                                title="Reset Password"
                                data-testid={`reset-password-${u.id}`}
                              >
                                <KeyRound className="w-4 h-4" />
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleToggleUserStatus(u.id, u.is_active)}
                                disabled={u.id === user?.id}
                                title={u.is_active ? "Deactivate" : "Activate"}
                              >
                                {u.is_active ? "Deactivate" : "Activate"}
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="text-red-600 hover:text-red-700"
                                onClick={() => handleDeleteUser(u.id)}
                                disabled={u.id === user?.id}
                                title="Delete User"
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <Shield className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                <p className="text-lg font-medium text-slate-700">Access Restricted</p>
                <p className="text-slate-500">Only administrators can manage users</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* General Tab */}
        <TabsContent value="general">
          <Card>
            <CardHeader>
              <CardTitle>General Settings</CardTitle>
              <CardDescription>System configuration and preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Profile Info */}
              <div className="space-y-4">
                <h3 className="font-semibold text-lg">Your Profile</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-slate-500">Name</Label>
                    <p className="font-medium">{user?.name}</p>
                  </div>
                  <div>
                    <Label className="text-slate-500">Email</Label>
                    <p className="font-medium">{user?.email}</p>
                  </div>
                  <div>
                    <Label className="text-slate-500">Role</Label>
                    <Badge className={getRoleBadge(user?.role)}>{user?.role}</Badge>
                  </div>
                  <div>
                    <Label className="text-slate-500">Phone</Label>
                    <p className="font-medium">{user?.phone || "-"}</p>
                  </div>
                </div>
              </div>

              {/* API Integration Info */}
              <div className="space-y-4">
                <h3 className="font-semibold text-lg">Integration Status</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <span>Google Forms Webhook</span>
                      <Badge variant="outline">Ready</Badge>
                    </div>
                    <p className="text-sm text-slate-500 mt-1">
                      Endpoint: /api/webhook/google-form
                    </p>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <span>Email (SendGrid)</span>
                      <Badge className="bg-green-100 text-green-700">Active</Badge>
                    </div>
                    <p className="text-sm text-slate-500 mt-1">
                      Email service configured and ready
                    </p>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <span>WhatsApp (Twilio)</span>
                      <Badge className="bg-amber-100 text-amber-700">Pending</Badge>
                    </div>
                    <p className="text-sm text-slate-500 mt-1">
                      Configure Twilio credentials for production
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Edit User Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Edit className="w-5 h-5 text-primary" />
              Edit User
            </DialogTitle>
            <DialogDescription>
              Update user details and permissions
            </DialogDescription>
          </DialogHeader>
          {editingUser && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Full Name</Label>
                <Input
                  value={editingUser.name}
                  onChange={(e) => setEditingUser({ ...editingUser, name: e.target.value })}
                  data-testid="edit-user-name"
                />
              </div>
              <div className="space-y-2">
                <Label>Email</Label>
                <Input
                  value={editingUser.email}
                  disabled
                  className="bg-slate-50"
                />
                <p className="text-xs text-slate-500">Email cannot be changed</p>
              </div>
              <div className="space-y-2">
                <Label>Phone</Label>
                <Input
                  value={editingUser.phone || ""}
                  onChange={(e) => setEditingUser({ ...editingUser, phone: e.target.value })}
                  placeholder="9876543210"
                  data-testid="edit-user-phone"
                />
              </div>
              <div className="space-y-2">
                <Label>Role</Label>
                <Select
                  value={editingUser.role}
                  onValueChange={(value) => setEditingUser({ ...editingUser, role: value })}
                >
                  <SelectTrigger data-testid="edit-user-role">
                    <SelectValue />
                  </SelectTrigger>
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
                <Select
                  value={editingUser.is_active ? "active" : "inactive"}
                  onValueChange={(value) => setEditingUser({ ...editingUser, is_active: value === "active" })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="inactive">Inactive</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex gap-2 pt-4">
                <Button
                  variant="outline"
                  onClick={() => setEditDialogOpen(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleSaveUserEdit}
                  disabled={saving}
                  className="flex-1"
                  data-testid="save-edit-user-btn"
                >
                  {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                  Save Changes
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Reset Password Dialog */}
      <Dialog open={resetPasswordDialogOpen} onOpenChange={setResetPasswordDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <KeyRound className="w-5 h-5 text-primary" />
              Reset Password
            </DialogTitle>
            <DialogDescription>
              Set a new password for this user
            </DialogDescription>
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
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Minimum 6 characters"
                    className="pr-10"
                    data-testid="admin-new-password"
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
                <Label>Confirm Password</Label>
                <Input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Re-enter new password"
                  data-testid="admin-confirm-password"
                />
              </div>
              
              <div className="flex gap-2 pt-4">
                <Button
                  variant="outline"
                  onClick={() => setResetPasswordDialogOpen(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleResetPassword}
                  disabled={resettingPassword || !newPassword || !confirmPassword}
                  className="flex-1"
                  data-testid="admin-reset-password-btn"
                >
                  {resettingPassword ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                  Reset Password
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default SettingsPage;
