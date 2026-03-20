import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
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
  DialogFooter,
} from "../components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../components/ui/alert-dialog";
import { toast } from "sonner";
import {
  Plus,
  Search,
  Eye,
  Filter,
  Users,
  Loader2,
  Trash2,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CustomersPage = () => {
  const navigate = useNavigate();
  const [customers, setCustomers] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [projectFilter, setProjectFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [agreementFilter, setAgreementFilter] = useState("");
  const [projects, setProjects] = useState([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [customerToDelete, setCustomerToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    email: "",
    father_name: "",
    pan_number: "",
    project: "",
    tower: "",
    unit_number: "",
    saleable_area: "",
    parking: "",
    total_price: "",
    booking_amount: "",
    booking_date: "",
  });

  useEffect(() => {
    fetchCustomers();
    fetchProjects();
  }, [search, projectFilter, statusFilter, agreementFilter]);

  const fetchCustomers = async () => {
    try {
      const params = new URLSearchParams();
      if (search) params.append("search", search);
      if (projectFilter) params.append("project", projectFilter);
      if (statusFilter) params.append("agreement_status", statusFilter);
      if (agreementFilter) params.append("agreement_filter", agreementFilter);

      const response = await axios.get(`${API}/customers?${params.toString()}`);
      setCustomers(response.data.customers);
      setTotal(response.data.total);
    } catch (error) {
      toast.error("Failed to fetch customers");
    } finally {
      setLoading(false);
    }
  };

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects`);
      setProjects(response.data);
    } catch (error) {
      console.error("Failed to fetch projects:", error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const payload = {
        ...formData,
        saleable_area: parseFloat(formData.saleable_area) || 0,
        total_price: parseFloat(formData.total_price) || 0,
        booking_amount: parseFloat(formData.booking_amount) || 0,
      };

      await axios.post(`${API}/customers`, payload);
      toast.success("Customer created successfully");
      setIsDialogOpen(false);
      setFormData({
        name: "",
        phone: "",
        email: "",
        father_name: "",
        pan_number: "",
        project: "",
        tower: "",
        unit_number: "",
        saleable_area: "",
        parking: "",
        total_price: "",
        booking_amount: "",
        booking_date: "",
      });
      fetchCustomers();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to create customer");
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      draft: "bg-slate-100 text-slate-700",
      sent: "bg-blue-100 text-blue-700",
      signed: "bg-green-100 text-green-700",
      completed: "bg-purple-100 text-purple-700",
    };
    return styles[status] || styles.draft;
  };

  const handleDeleteClick = (customer, e) => {
    e.stopPropagation();
    setCustomerToDelete(customer);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!customerToDelete) return;
    
    setDeleting(true);
    try {
      await axios.delete(`${API}/customers/${customerToDelete.id}`);
      toast.success(`Customer ${customerToDelete.name} deleted successfully`);
      setDeleteDialogOpen(false);
      setCustomerToDelete(null);
      fetchCustomers();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to delete customer");
    } finally {
      setDeleting(false);
    }
  };

  const handleAgreementStatusChange = async (customerId, newStatus) => {
    try {
      await axios.put(`${API}/customers/${customerId}`, {
        agreement_status: newStatus
      });
      toast.success(`Agreement status updated to ${newStatus}`);
      // Update local state
      setCustomers(customers.map(c => 
        c.id === customerId ? { ...c, agreement_status: newStatus } : c
      ));
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to update agreement status");
    }
  };

  return (
    <div className="space-y-6" data-testid="customers-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="font-heading text-3xl font-bold text-slate-900">Customers</h1>
          <p className="text-slate-500 mt-1">Manage all your customer profiles</p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button data-testid="add-customer-btn">
              <Plus className="w-4 h-4 mr-2" />
              Add Customer
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="font-heading">Add New Customer</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Customer Name *</Label>
                  <Input
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    data-testid="customer-name-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email *</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                    data-testid="customer-email-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone *</Label>
                  <Input
                    id="phone"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    required
                    data-testid="customer-phone-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="father_name">Father's Name</Label>
                  <Input
                    id="father_name"
                    name="father_name"
                    value={formData.father_name}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="pan_number">PAN Number</Label>
                  <Input
                    id="pan_number"
                    name="pan_number"
                    value={formData.pan_number}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="project">Project *</Label>
                  <Select
                    value={formData.project}
                    onValueChange={(value) => setFormData((prev) => ({ ...prev, project: value }))}
                  >
                    <SelectTrigger data-testid="customer-project-select">
                      <SelectValue placeholder="Select project" />
                    </SelectTrigger>
                    <SelectContent>
                      {projects.map((project) => (
                        <SelectItem key={project.name} value={project.name}>
                          {project.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="tower">Tower *</Label>
                  <Input
                    id="tower"
                    name="tower"
                    value={formData.tower}
                    onChange={handleInputChange}
                    required
                    data-testid="customer-tower-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="unit_number">Unit Number *</Label>
                  <Input
                    id="unit_number"
                    name="unit_number"
                    value={formData.unit_number}
                    onChange={handleInputChange}
                    required
                    data-testid="customer-unit-input"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="saleable_area">Saleable Area (sq.ft)</Label>
                  <Input
                    id="saleable_area"
                    name="saleable_area"
                    type="number"
                    value={formData.saleable_area}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="parking">Parking</Label>
                  <Input
                    id="parking"
                    name="parking"
                    value={formData.parking}
                    onChange={handleInputChange}
                    placeholder="e.g., 1 Covered"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="total_price">Total Price (₹)</Label>
                  <Input
                    id="total_price"
                    name="total_price"
                    type="number"
                    value={formData.total_price}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="booking_amount">Booking Amount (₹)</Label>
                  <Input
                    id="booking_amount"
                    name="booking_amount"
                    type="number"
                    value={formData.booking_amount}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="booking_date">Booking Date</Label>
                  <Input
                    id="booking_date"
                    name="booking_date"
                    type="date"
                    value={formData.booking_date}
                    onChange={handleInputChange}
                  />
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={submitting} data-testid="submit-customer-btn">
                  {submitting ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    "Create Customer"
                  )}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                placeholder="Search by name, email, phone, or ID..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
                data-testid="search-customers-input"
              />
            </div>
            <Select value={projectFilter || "all"} onValueChange={(v) => setProjectFilter(v === "all" ? "" : v)}>
              <SelectTrigger className="w-full sm:w-48" data-testid="filter-project-select">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="All Projects" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Projects</SelectItem>
                {projects.map((project) => (
                  <SelectItem key={project.name} value={project.name}>
                    {project.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={statusFilter || "all"} onValueChange={(v) => setStatusFilter(v === "all" ? "" : v)}>
              <SelectTrigger className="w-full sm:w-48" data-testid="filter-status-select">
                <SelectValue placeholder="All Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="sent">Sent</SelectItem>
                <SelectItem value="signed">Signed</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
              </SelectContent>
            </Select>
            <Select value={agreementFilter || "all"} onValueChange={(v) => setAgreementFilter(v === "all" ? "" : v)}>
              <SelectTrigger className="w-full sm:w-52" data-testid="filter-agreement-select">
                <SelectValue placeholder="Agreement Filter" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Agreements</SelectItem>
                <SelectItem value="upcoming_due">Upcoming Due (Next 5 Days)</SelectItem>
                <SelectItem value="pending_agreement">Pending Agreement</SelectItem>
                <SelectItem value="agreement_due">Agreement Signing Due</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="flex items-center gap-2 text-sm text-slate-500">
        <Users className="w-4 h-4" />
        <span>
          Showing {customers.length} of {total} customers
        </span>
      </div>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : customers.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Customer ID</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Project</TableHead>
                  <TableHead>Flat No.</TableHead>
                  <TableHead>Unit</TableHead>
                  <TableHead>Phone</TableHead>
                  <TableHead>Agreement</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {customers.map((customer) => (
                  <TableRow
                    key={customer.id}
                    className="cursor-pointer hover:bg-slate-50"
                    onClick={() => navigate(`/customers/${customer.id}`)}
                    data-testid={`customer-row-${customer.id}`}
                  >
                    <TableCell className="font-mono text-sm">{customer.customer_id}</TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{customer.name}</p>
                        <p className="text-sm text-slate-500">{customer.email}</p>
                      </div>
                    </TableCell>
                    <TableCell>{customer.project}</TableCell>
                    <TableCell>
                      <span className="font-mono font-medium text-blue-600">
                        {customer.unit_number}
                      </span>
                    </TableCell>
                    <TableCell>
                      <span className="font-mono">
                        {customer.tower}-{customer.unit_number}
                      </span>
                    </TableCell>
                    <TableCell>{customer.phone}</TableCell>
                    <TableCell onClick={(e) => e.stopPropagation()}>
                      <Select
                        value={customer.agreement_status || 'draft'}
                        onValueChange={(value) => handleAgreementStatusChange(customer.id, value)}
                      >
                        <SelectTrigger className={`w-28 h-8 text-xs ${getStatusBadge(customer.agreement_status)}`}>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="draft">Draft</SelectItem>
                          <SelectItem value="sent">Sent</SelectItem>
                          <SelectItem value="signed">Signed</SelectItem>
                          <SelectItem value="registered">Registered</SelectItem>
                        </SelectContent>
                      </Select>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/customers/${customer.id}`);
                          }}
                          data-testid={`view-customer-${customer.id}`}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          onClick={(e) => handleDeleteClick(customer, e)}
                          data-testid={`delete-customer-${customer.id}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-slate-500">
              <Users className="w-12 h-12 mb-4 text-slate-300" />
              <p className="text-lg font-medium">No customers found</p>
              <p className="text-sm">Try adjusting your search or filters</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure you want to delete this customer?</AlertDialogTitle>
            <AlertDialogDescription>
              {customerToDelete && (
                <>
                  You are about to delete <strong>{customerToDelete.name}</strong> ({customerToDelete.customer_id}).
                  <br /><br />
                  This action will permanently delete:
                  <ul className="list-disc list-inside mt-2 text-sm">
                    <li>All customer details and profile information</li>
                    <li>Payment schedule and history</li>
                    <li>All generated documents</li>
                    <li>Communication logs</li>
                  </ul>
                  <br />
                  <strong className="text-red-600">This action cannot be undone.</strong>
                </>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDelete}
              disabled={deleting}
              className="bg-red-600 hover:bg-red-700"
              data-testid="confirm-delete-customer-btn"
            >
              {deleting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Deleting...
                </>
              ) : (
                <>
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete Customer
                </>
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default CustomersPage;
