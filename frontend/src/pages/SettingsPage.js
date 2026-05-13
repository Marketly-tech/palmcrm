import { useState, useEffect } from "react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import { Card, CardContent } from "../components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { toast } from "sonner";
import { Users, Settings, Shield, FileText } from "lucide-react";
import {
  UserManagementCard, EditUserDialog, ResetPasswordDialog, GeneralSettingsTab,
  DocumentTemplatesTab,
} from "../components/settings";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getRoleBadge = (role) => {
  const styles = { admin: "bg-red-100 text-red-700", manager: "bg-purple-100 text-purple-700", accounts: "bg-blue-100 text-blue-700", sales: "bg-green-100 text-green-700", support: "bg-yellow-100 text-yellow-700" };
  return styles[role] || "bg-slate-100 text-slate-700";
};

const getRoleDescription = (role) => {
  const descriptions = { admin: "Full access to all features including user management", manager: "Can manage customers, leads, and view reports", accounts: "Can manage payments and financial documents", sales: "Can view and update customer information", support: "Limited access to customer support features" };
  return descriptions[role] || "Standard user access";
};

const SettingsPage = () => {
  const { user, hasRole } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Create user
  const [userDialogOpen, setUserDialogOpen] = useState(false);
  const [newUser, setNewUser] = useState({ name: "", email: "", password: "", role: "sales", phone: "" });

  // Edit user
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  // Reset password
  const [resetPasswordDialogOpen, setResetPasswordDialogOpen] = useState(false);
  const [resetPasswordUser, setResetPasswordUser] = useState(null);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [resettingPassword, setResettingPassword] = useState(false);

  useEffect(() => {
    if (hasRole("admin")) fetchUsers();
    else setLoading(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      setUsers(response.data);
    } catch { toast.error("Failed to fetch users"); }
    finally { setLoading(false); }
  };

  const handleCreateUser = async () => {
    if (!newUser.name || !newUser.email || !newUser.password) { toast.error("Please fill all required fields"); return; }
    setSaving(true);
    try {
      await axios.post(`${API}/auth/register`, newUser);
      fetchUsers();
      setUserDialogOpen(false);
      setNewUser({ name: "", email: "", password: "", role: "sales", phone: "" });
      toast.success("User created successfully");
    } catch (error) { toast.error(error.response?.data?.detail || "Failed to create user"); }
    finally { setSaving(false); }
  };

  const handleSaveUserEdit = async () => {
    if (!editingUser) return;
    setSaving(true);
    try {
      await axios.put(`${API}/users/${editingUser.id}`, { name: editingUser.name, role: editingUser.role, phone: editingUser.phone, is_active: editingUser.is_active });
      fetchUsers();
      setEditDialogOpen(false);
      setEditingUser(null);
      toast.success("User updated successfully");
    } catch (error) { toast.error(error.response?.data?.detail || "Failed to update user"); }
    finally { setSaving(false); }
  };

  const handleResetPassword = async () => {
    if (!resetPasswordUser) return;
    if (newPassword.length < 6) { toast.error("Password must be at least 6 characters"); return; }
    if (newPassword !== confirmPassword) { toast.error("Passwords do not match"); return; }
    setResettingPassword(true);
    try {
      await axios.post(`${API}/admin/reset-user-password`, { user_id: resetPasswordUser.id, new_password: newPassword });
      setResetPasswordDialogOpen(false);
      setResetPasswordUser(null);
      setNewPassword("");
      setConfirmPassword("");
      toast.success(`Password reset successfully for ${resetPasswordUser.name}`);
    } catch (error) { toast.error(error.response?.data?.detail || "Failed to reset password"); }
    finally { setResettingPassword(false); }
  };

  const handleToggleUserStatus = async (userId, isActive) => {
    try {
      await axios.put(`${API}/users/${userId}`, { is_active: !isActive });
      fetchUsers();
      toast.success(`User ${isActive ? "deactivated" : "activated"}`);
    } catch { toast.error("Failed to update user"); }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm("Are you sure you want to delete this user?")) return;
    try {
      await axios.delete(`${API}/users/${userId}`);
      fetchUsers();
      toast.success("User deleted");
    } catch { toast.error("Failed to delete user"); }
  };

  return (
    <div className="space-y-6" data-testid="settings-page">
      <div>
        <h1 className="font-heading text-3xl font-bold text-slate-900">Settings</h1>
        <p className="text-slate-500 mt-1">Manage users and system settings</p>
      </div>

      <Tabs defaultValue="users" className="space-y-4">
        <TabsList>
          <TabsTrigger value="users" data-testid="tab-users"><Users className="w-4 h-4 mr-2" />User Management</TabsTrigger>
          <TabsTrigger value="templates" data-testid="tab-templates"><FileText className="w-4 h-4 mr-2" />Document Templates</TabsTrigger>
          <TabsTrigger value="general" data-testid="tab-general"><Settings className="w-4 h-4 mr-2" />General</TabsTrigger>
        </TabsList>

        <TabsContent value="users">
          {hasRole("admin") ? (
            <UserManagementCard
              users={users} loading={loading} currentUserId={user?.id}
              userDialogOpen={userDialogOpen} setUserDialogOpen={setUserDialogOpen}
              newUser={newUser} setNewUser={setNewUser} saving={saving}
              onCreateUser={handleCreateUser}
              onEditUser={(u) => { setEditingUser({ ...u }); setEditDialogOpen(true); }}
              onResetPassword={(u) => { setResetPasswordUser(u); setNewPassword(""); setConfirmPassword(""); setShowNewPassword(false); setResetPasswordDialogOpen(true); }}
              onToggleStatus={handleToggleUserStatus}
              onDeleteUser={handleDeleteUser}
              getRoleBadge={getRoleBadge}
            />
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

        <TabsContent value="general">
          <GeneralSettingsTab user={user} getRoleBadge={getRoleBadge} />
        </TabsContent>

        <TabsContent value="templates">
          {hasRole("admin") ? (
            <DocumentTemplatesTab />
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <Shield className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                <p className="text-lg font-medium text-slate-700">Access Restricted</p>
                <p className="text-slate-500">Only administrators can edit document templates</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      <EditUserDialog
        open={editDialogOpen} onOpenChange={setEditDialogOpen}
        editingUser={editingUser} setEditingUser={setEditingUser}
        saving={saving} onSave={handleSaveUserEdit} getRoleDescription={getRoleDescription}
      />

      <ResetPasswordDialog
        open={resetPasswordDialogOpen} onOpenChange={setResetPasswordDialogOpen}
        resetPasswordUser={resetPasswordUser}
        newPassword={newPassword} setNewPassword={setNewPassword}
        confirmPassword={confirmPassword} setConfirmPassword={setConfirmPassword}
        showNewPassword={showNewPassword} setShowNewPassword={setShowNewPassword}
        resettingPassword={resettingPassword} onReset={handleResetPassword}
      />
    </div>
  );
};

export default SettingsPage;
