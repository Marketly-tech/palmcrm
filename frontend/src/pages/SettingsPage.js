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
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SettingsPage = () => {
  const { user, hasRole } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userDialogOpen, setUserDialogOpen] = useState(false);
  const [saving, setSaving] = useState(false);

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
                        <TableHead>Actions</TableHead>
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
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleToggleUserStatus(u.id, u.is_active)}
                                disabled={u.id === user?.id}
                              >
                                {u.is_active ? "Deactivate" : "Activate"}
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="text-red-600 hover:text-red-700"
                                onClick={() => handleDeleteUser(u.id)}
                                disabled={u.id === user?.id}
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
                      <Badge className="bg-amber-100 text-amber-700">MOCKED</Badge>
                    </div>
                    <p className="text-sm text-slate-500 mt-1">
                      Configure SendGrid API key for production
                    </p>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <span>WhatsApp (Twilio)</span>
                      <Badge className="bg-amber-100 text-amber-700">MOCKED</Badge>
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
    </div>
  );
};

export default SettingsPage;
