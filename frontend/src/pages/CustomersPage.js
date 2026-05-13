import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from "../components/ui/alert-dialog";
import { toast } from "sonner";
import { Users, Loader2, Trash2 } from "lucide-react";
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
  const [banks, setBanks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState(EMPTY_FORM);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [customerToDelete, setCustomerToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    fetchCustomers();
    fetchProjects();
    fetchBanks();
  }, [search, projectFilter, statusFilter, agreementFilter, bankFilter]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchCustomers = async () => {
    try {
      const params = new URLSearchParams();
      if (search) params.append("search", search);
      if (projectFilter) params.append("project", projectFilter);
      if (statusFilter) params.append("agreement_status", statusFilter);
      if (agreementFilter) params.append("agreement_filter", agreementFilter);
      if (bankFilter) params.append("finance_bank", bankFilter);
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
        projects={projects} total={total}
      />

      <div className="flex items-center gap-2 text-sm text-slate-500">
        <Users className="w-4 h-4" />
        <span>Showing {customers.length} of {total} customers</span>
      </div>

      <CustomerTable
        customers={customers} loading={loading} isAccountsRole={isAccountsRole}
        agreementFilter={agreementFilter} bankFilter={bankFilter}
        onNavigate={navigate}
        onDeleteClick={(customer, e) => { e.stopPropagation(); setCustomerToDelete(customer); setDeleteDialogOpen(true); }}
        onAgreementStatusChange={handleAgreementStatusChange}
      />

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
