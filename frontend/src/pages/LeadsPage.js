import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { openSafePreviewWindow } from "../utils/safePreview";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
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
import { toast } from "sonner";
import {
  UserPlus,
  CheckCircle,
  XCircle,
  Eye,
  Loader2,
  Clock,
  Mail,
  Send,
  ExternalLink,
  Edit,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LeadsPage = () => {
  const navigate = useNavigate();
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedLead, setSelectedLead] = useState(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [sendingWelcome, setSendingWelcome] = useState({});
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [leadToReject, setLeadToReject] = useState(null);
  const [rejectReason, setRejectReason] = useState("");

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      const response = await axios.get(`${API}/leads/pending`);
      setLeads(response.data);
    } catch (error) {
      toast.error("Failed to fetch pending leads");
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (lead) => {
    setProcessing(true);
    try {
      await axios.put(`${API}/leads/${lead.id}/approve`);
      toast.success(`${lead.name} has been approved!`);
      fetchLeads();
      setViewDialogOpen(false);
    } catch (error) {
      toast.error(error?.response?.data?.detail || "Failed to approve lead");
    } finally {
      setProcessing(false);
    }
  };

  const openRejectDialog = (lead) => {
    setLeadToReject(lead);
    setRejectReason("");
    setRejectDialogOpen(true);
  };

  const handleReject = async () => {
    if (!leadToReject) return;
    setProcessing(true);
    try {
      await axios.put(`${API}/leads/${leadToReject.id}/reject`, null, {
        params: rejectReason ? { reason: rejectReason } : {},
      });
      toast.success(`${leadToReject.name} has been rejected and removed.`);
      fetchLeads();
      setRejectDialogOpen(false);
      setViewDialogOpen(false);
      setLeadToReject(null);
      setRejectReason("");
    } catch (error) {
      toast.error(error?.response?.data?.detail || "Failed to reject lead");
    } finally {
      setProcessing(false);
    }
  };

  const handleEditLead = (lead) => {
    // Navigate to customer detail page for editing
    navigate(`/customers/${lead.id}`);
    toast.info("You can edit the lead details here");
  };

  const handleSendWelcomeEmail = async (lead) => {
    setSendingWelcome(prev => ({ ...prev, [lead.id]: true }));
    try {
      const response = await axios.post(`${API}/communication/send-welcome-email/${lead.id}`);
      toast.success(`Welcome email sent to ${lead.email} (MOCKED)`);
      
      // Show the generated content
      if (response.data.welcome_html) {
        openSafePreviewWindow(response.data.welcome_html);
      }
      
      fetchLeads();
    } catch (error) {
      toast.error("Failed to send welcome email");
    } finally {
      setSendingWelcome(prev => ({ ...prev, [lead.id]: false }));
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount || 0);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "-";
    try {
      return new Date(dateStr).toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      });
    } catch {
      return dateStr;
    }
  };

  const copyBookingFormLink = () => {
    const link = `${window.location.origin}/booking-form`;
    navigator.clipboard.writeText(link);
    toast.success("Booking form link copied to clipboard!");
  };

  return (
    <div className="space-y-6" data-testid="leads-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="font-heading text-3xl font-bold text-slate-900">Pending Leads</h1>
          <p className="text-slate-500 mt-1">Review and approve new booking submissions</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={copyBookingFormLink} data-testid="copy-form-link-btn">
            <ExternalLink className="w-4 h-4 mr-2" />
            Copy Booking Form Link
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4 flex items-center gap-4">
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Pending Approval</p>
              <p className="text-2xl font-bold">{leads.length}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Leads Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <UserPlus className="w-5 h-5 text-primary" />
            New Booking Submissions
          </CardTitle>
          <CardDescription>
            Leads submitted through the booking form awaiting approval
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {(() => {
            if (loading) {
              return (
                <div className="flex items-center justify-center h-64">
                  <Loader2 className="w-8 h-8 animate-spin text-primary" />
                </div>
              );
            }
            if (leads.length === 0) {
              return (
                <div className="text-center py-16 text-slate-500">
                  <UserPlus className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                  <p className="text-lg">No new leads</p>
                  <p className="text-sm mt-1">Leads from the public booking form will appear here</p>
                </div>
              );
            }
            return (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Customer</TableHead>
                    <TableHead>Project</TableHead>
                    <TableHead>Unit</TableHead>
                    <TableHead>Booking Amount</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {leads.map((lead) => (
                  <TableRow key={lead.id} data-testid={`lead-row-${lead.id}`}>
                    <TableCell>
                      <div>
                        <p className="font-medium">{lead.name}</p>
                        <p className="text-sm text-slate-500">{lead.phone}</p>
                      </div>
                    </TableCell>
                    <TableCell>{lead.project}</TableCell>
                    <TableCell>
                      <span className="font-mono">{lead.tower}-{lead.unit_number}</span>
                    </TableCell>
                    <TableCell>{formatCurrency(lead.booking_amount)}</TableCell>
                    <TableCell>{formatDate(lead.booking_date)}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedLead(lead);
                            setViewDialogOpen(true);
                          }}
                          data-testid={`view-lead-${lead.id}`}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                          onClick={() => handleEditLead(lead)}
                          data-testid={`edit-lead-${lead.id}`}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-green-600 hover:text-green-700 hover:bg-green-50"
                          onClick={() => handleApprove(lead)}
                          disabled={processing}
                          data-testid={`approve-lead-${lead.id}`}
                          title="Approve lead"
                        >
                          <CheckCircle className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          onClick={() => openRejectDialog(lead)}
                          disabled={processing}
                          data-testid={`reject-lead-${lead.id}`}
                          title="Reject lead"
                        >
                          <XCircle className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
                </TableBody>
              </Table>
            );
          })()}
        </CardContent>
      </Card>

      {/* View Lead Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Lead Details</DialogTitle>
            <DialogDescription>Review the booking submission details</DialogDescription>
          </DialogHeader>
          
          {selectedLead && (
            <div className="space-y-6">
              {/* Applicant Info */}
              <div className="bg-slate-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-3">Applicant Information</h3>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <p className="text-slate-500">Name:</p>
                  <p className="font-medium">{selectedLead.name}</p>
                  <p className="text-slate-500">Phone:</p>
                  <p className="font-medium">{selectedLead.phone}</p>
                  <p className="text-slate-500">Email:</p>
                  <p className="font-medium">{selectedLead.email}</p>
                  {selectedLead.father_name && (
                    <>
                      <p className="text-slate-500">Father's Name:</p>
                      <p className="font-medium">{selectedLead.father_name}</p>
                    </>
                  )}
                  {selectedLead.pan_number && (
                    <>
                      <p className="text-slate-500">PAN:</p>
                      <p className="font-medium">{selectedLead.pan_number}</p>
                    </>
                  )}
                  {selectedLead.aadhar_number && (
                    <>
                      <p className="text-slate-500">Aadhaar:</p>
                      <p className="font-medium">{selectedLead.aadhar_number}</p>
                    </>
                  )}
                </div>
              </div>

              {/* Property Info */}
              <div className="bg-slate-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-3">Property Details</h3>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <p className="text-slate-500">Project:</p>
                  <p className="font-medium">{selectedLead.project}</p>
                  <p className="text-slate-500">Tower:</p>
                  <p className="font-medium">{selectedLead.tower}</p>
                  <p className="text-slate-500">Unit Number:</p>
                  <p className="font-medium">{selectedLead.unit_number}</p>
                  <p className="text-slate-500">BHK:</p>
                  <p className="font-medium">{selectedLead.bhk_type || "-"}</p>
                  <p className="text-slate-500">Saleable Area:</p>
                  <p className="font-medium">{selectedLead.saleable_area || 0} sq.ft</p>
                  <p className="text-slate-500">Total Price:</p>
                  <p className="font-medium text-primary">{formatCurrency(selectedLead.total_price)}</p>
                </div>
              </div>

              {/* Payment Info */}
              <div className="bg-slate-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-3">Payment Information</h3>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <p className="text-slate-500">Booking Amount:</p>
                  <p className="font-medium">{formatCurrency(selectedLead.booking_amount)}</p>
                  <p className="text-slate-500">Booking Date:</p>
                  <p className="font-medium">{formatDate(selectedLead.booking_date)}</p>
                  <p className="text-slate-500">Finance Type:</p>
                  <p className="font-medium capitalize">{selectedLead.finance_type || "Self"}</p>
                  {selectedLead.transaction_details && (
                    <>
                      <p className="text-slate-500">Transaction:</p>
                      <p className="font-medium">{selectedLead.transaction_details}</p>
                    </>
                  )}
                </div>
              </div>

              {selectedLead.remarks && (
                <div className="bg-amber-50 p-4 rounded-lg">
                  <h3 className="font-semibold mb-2">Remarks</h3>
                  <p className="text-sm">{selectedLead.remarks}</p>
                </div>
              )}

              <DialogFooter className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => handleEditLead(selectedLead)}
                  className="text-blue-600"
                >
                  <Edit className="w-4 h-4 mr-2" />
                  Edit
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handleSendWelcomeEmail(selectedLead)}
                  disabled={sendingWelcome[selectedLead.id]}
                >
                  {sendingWelcome[selectedLead.id] ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Mail className="w-4 h-4 mr-2" />
                  )}
                  Send Welcome Email
                </Button>
                <Button
                  onClick={() => handleApprove(selectedLead)}
                  disabled={processing}
                  data-testid="confirm-approve-btn"
                >
                  {processing ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <CheckCircle className="w-4 h-4 mr-2" />
                  )}
                  Approve
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => openRejectDialog(selectedLead)}
                  disabled={processing}
                  data-testid="confirm-reject-btn"
                >
                  <XCircle className="w-4 h-4 mr-2" />
                  Reject
                </Button>
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Reject Lead Confirmation Dialog */}
      <Dialog open={rejectDialogOpen} onOpenChange={setRejectDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject Lead?</DialogTitle>
            <DialogDescription>
              {leadToReject ? (
                <>This will permanently delete <strong>{leadToReject.name}</strong>'s
                booking submission and release the assigned unit
                ({leadToReject.tower}-{leadToReject.unit_number}) back to available.
                This action cannot be undone.</>
              ) : "This action cannot be undone."}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2">
            <label htmlFor="reject-reason" className="text-sm font-medium">
              Reason <span className="text-red-600">*</span>
            </label>
            <Input
              id="reject-reason"
              data-testid="reject-reason-input"
              placeholder="e.g. Duplicate submission, customer withdrew, etc."
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              required
            />
            <p className="text-xs text-slate-500">A reason is required so the rejection is auditable.</p>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setRejectDialogOpen(false)}
              disabled={processing}
              data-testid="reject-cancel-btn"
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleReject}
              disabled={processing || !rejectReason.trim()}
              data-testid="reject-confirm-btn"
            >
              {processing ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <XCircle className="w-4 h-4 mr-2" />
              )}
              Confirm Reject
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default LeadsPage;
