import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from "../components/ui/alert-dialog";
import { Button } from "../components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { toast } from "sonner";
import { Users, Loader2, Trash2, ChevronLeft, ChevronRight } from "lucide-react";
import { CreateCustomerDialog, CustomerFilters, CustomerTable } from "../components/customers";
import { logError } from "../utils/logger";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EMPTY_FORM = {
  name: "", phone: "", email: "", father_name: "", pan_number: "",
  project: "", tower: "", unit_number: "", saleable_area: "",
  parking: "", total_price: "", booking_amount: "", booking_date: "",
};

const CustomersPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const isAccountsRole = user?.role === "accounts";

  const [customers, setCustomers] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [projectFilter, setProjectFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [agreementFilter, setAgreementFilter] = useState("");
  const [bankFilter, setBankFilter] = useState("");
  const [callStatusFilter, setCallStatusFilter] = useState("");
  const [banks, setBanks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState(EMPTY_FORM);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [customerToDelete, setCustomerToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  // Pagination state — backend default was capping at 50, causing rows beyond
  // 50 to be invisible. We now drive `skip`/`limit` explicitly and expose
  // Prev/Next + page-size controls below the table.
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(50);

  // Reset to page 1 whenever any filter changes so the user doesn't end up on
  // an empty page after narrowing the result set.
  useEffect(() => {
    setPage(0);
  }, [search, projectFilter, statusFilter, agreementFilter, bankFilter, callStatusFilter, pageSize]);

  useEffect(() => {
    fetchCustomers();
    fetchProjects();
    fetchBanks();
  }, [search, projectFilter, statusFilter, agreementFilter, bankFilter, callStatusFilter, page, pageSize]);

  const fetchCustomers = async () => {
    try {
      const params = new URLSearchParams();
      if (search) params.append("search", search);
      if (projectFilter) params.append("project", projectFilter);
      if (statusFilter) params.append("agreement_status", statusFilter);
      if (agreementFilter) params.append("agreement_filter", agreementFilter);
      if (bankFilter) params.append("finance_bank", bankFilter);
      if (callStatusFilter) params.append("call_status", callStatusFilter);
      params.append("skip", String(page * pageSize));
      params.append("limit", String(pageSize));
      const response = await axios.get(`${API}/customers?${params.toString()}`);
      setCustomers(response.data.customers);
      setTotal(response.data.total);
    } catch { toast.error("Failed to fetch customers"); }
    finally { setLoading(false); }
  };

  const fetchProjects = async () => {
    try { const response = await axios.get(`${API}/projects`); setProjects(response.data); }
    catch (error) { logError("Failed to fetch projects:", error); }
  };

  const fetchBanks = async () => {
    try { const response = await axios.get(`${API}/customers/banks`); setBanks(response.data); }
    catch (error) { logError("Failed to fetch banks:", error); }
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
      setFormData(EMPTY_FORM);
      fetchCustomers();
    } catch (error) { toast.error(error.response?.data?.detail || "Failed to create customer"); }
    finally { setSubmitting(false); }
  };

  const handleAgreementStatusChange = async (customerId, newStatus) => {
    try {
      await axios.put(`${API}/customers/${customerId}`, { agreement_status: newStatus });
      toast.success(`Agreement status updated to ${newStatus}`);
      setCustomers(customers.map((c) => c.id === customerId ? { ...c, agreement_status: newStatus } : c));
    } catch (error) { toast.error(error.response?.data?.detail || "Failed to update agreement status"); }
  };

  const handleCallStatusChange = async (customerId, newStatus) => {
    try {
      const res = await axios.post(`${API}/customers/${customerId}/follow-ups/quick-status`, { status: newStatus });
      toast.success(`Call status set to ${newStatus}`);
      setCustomers(customers.map((c) => c.id === customerId ? {
        ...c,
        latest_call_status: newStatus,
        latest_call_status_at: res.data?.created_at,
        latest_call_status_stage: res.data?.stage_name,
      } : c));
    } catch (error) { toast.error(error.response?.data?.detail || "Failed to update call status"); }
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
    } catch (error) { toast.error(error.response?.data?.detail || "Failed to delete customer"); }
    finally { setDeleting(false); }
  };

  return (
    <div className="space-y-6" data-testid="customers-page">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="font-heading text-3xl font-bold text-slate-900">Customers</h1>
          <p className="text-slate-500 mt-1">Manage all your customer profiles</p>
        </div>
        <CreateCustomerDialog
          open={isDialogOpen} onOpenChange={setIsDialogOpen}
          formData={formData} setFormData={setFormData}
          projects={projects} submitting={submitting} onSubmit={handleSubmit}
        />
      </div>

      <CustomerFilters
        search={search} setSearch={setSearch}
        projectFilter={projectFilter} setProjectFilter={setProjectFilter}
        statusFilter={statusFilter} setStatusFilter={setStatusFilter}
        agreementFilter={agreementFilter} setAgreementFilter={setAgreementFilter}
        bankFilter={bankFilter} setBankFilter={setBankFilter} banks={banks}
        callStatusFilter={callStatusFilter} setCallStatusFilter={setCallStatusFilter}
        projects={projects} total={total}
      />

      <div className="flex items-center justify-between gap-2 text-sm text-slate-500">
        <div className="flex items-center gap-2">
          <Users className="w-4 h-4" />
          <span data-testid="customers-count-label">
            {total === 0
              ? "No customers"
              : `Showing ${page * pageSize + 1}–${Math.min(page * pageSize + customers.length, total)} of ${total} customers`}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500">Page size</span>
          <Select value={String(pageSize)} onValueChange={(v) => setPageSize(parseInt(v, 10))}>
            <SelectTrigger className="h-8 w-[80px]" data-testid="page-size-select">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {[25, 50, 100, 200, 500].map((s) => (
                <SelectItem key={s} value={String(s)}>{s}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <CustomerTable
        customers={customers} loading={loading} isAccountsRole={isAccountsRole}
        agreementFilter={agreementFilter} bankFilter={bankFilter}
        onNavigate={navigate}
        onDeleteClick={(customer, e) => { e.stopPropagation(); setCustomerToDelete(customer); setDeleteDialogOpen(true); }}
        onAgreementStatusChange={handleAgreementStatusChange}
        onCallStatusChange={handleCallStatusChange}
      />

      {total > pageSize && (
        <div className="flex items-center justify-between" data-testid="customers-pagination">
          <Button
            variant="outline"
            size="sm"
            disabled={page === 0 || loading}
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            data-testid="page-prev-btn"
          >
            <ChevronLeft className="w-4 h-4 mr-1" /> Previous
          </Button>
          <span className="text-xs text-slate-500" data-testid="page-indicator">
            Page {page + 1} of {Math.max(1, Math.ceil(total / pageSize))}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={(page + 1) * pageSize >= total || loading}
            onClick={() => setPage((p) => p + 1)}
            data-testid="page-next-btn"
          >
            Next <ChevronRight className="w-4 h-4 ml-1" />
          </Button>
        </div>
      )}

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure you want to delete this customer?</AlertDialogTitle>
            <AlertDialogDescription>
              {customerToDelete && (
                <>
                  You are about to delete <strong>{customerToDelete.name}</strong> ({customerToDelete.booking_number || customerToDelete.customer_id}).
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
            <AlertDialogAction onClick={handleConfirmDelete} disabled={deleting} className="bg-red-600 hover:bg-red-700" data-testid="confirm-delete-customer-btn">
              {deleting ? (<><Loader2 className="w-4 h-4 mr-2 animate-spin" />Deleting...</>) : (<><Trash2 className="w-4 h-4 mr-2" />Delete Customer</>)}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default CustomersPage;
