import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
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
import { Textarea } from "../components/ui/textarea";
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
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LeadsPage = () => {
  const navigate = useNavigate();
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedLead, setSelectedLead] = useState(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState("");
  const [processing, setProcessing] = useState(false);
  const [sendingWelcome, setSendingWelcome] = useState({});

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
      toast.error("Failed to approve lead");
    } finally {
      setProcessing(false);
    }
  };

  const handleReject = async () => {
    if (!selectedLead) return;
    
    setProcessing(true);
    try {
      await axios.put(`${API}/leads/${selectedLead.id}/reject?reason=${encodeURIComponent(rejectReason)}`);
      toast.success("Lead rejected");
      fetchLeads();
      setRejectDialogOpen(false);
      setViewDialogOpen(false);
      setRejectReason("");
    } catch (error) {
      toast.error("Failed to reject lead");
    } finally {
      setProcessing(false);
    }
  };

  const handleSendWelcomeEmail = async (lead) => {
    setSendingWelcome(prev => ({ ...prev, [lead.id]: true }));
    try {
      const response = await axios.post(`${API}/communication/send-welcome-email/${lead.id}`);
      toast.success(`Welcome email sent to ${lead.email} (MOCKED)`);
      
      // Show the generated content
      if (response.data.welcome_html) {
        // Open in new window for preview
        const previewWindow = window.open("", "_blank");
        if (previewWindow) {
          previewWindow.document.write(response.data.welcome_html);
          previewWindow.document.close();
        }
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
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : leads.length > 0 ? (
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
                          className="text-green-600 hover:text-green-700 hover:bg-green-50"
                          onClick={() => handleApprove(lead)}
                          disabled={processing}
                          data-testid={`approve-lead-${lead.id}`}
                        >
                          <CheckCircle className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          onClick={() => {
                            setSelectedLead(lead);
                            setRejectDialogOpen(true);
                          }}
                          data-testid={`reject-lead-${lead.id}`}
                        >
                          <XCircle className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-slate-500">
              <UserPlus className="w-12 h-12 mb-4 text-slate-300" />
              <p className="text-lg font-medium">No pending leads</p>
              <p className="text-sm">New booking submissions will appear here</p>
            </div>
          )}
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
                  onClick={() => {
                    setRejectDialogOpen(true);
                  }}
                  className="text-red-600"
                >
                  <XCircle className="w-4 h-4 mr-2" />
                  Reject
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
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Reject Dialog */}
      <Dialog open={rejectDialogOpen} onOpenChange={setRejectDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject Lead</DialogTitle>
            <DialogDescription>
              Are you sure you want to reject this booking? The unit will be released.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-slate-500 mb-2">Reason for rejection (optional)</p>
              <Textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="Enter reason..."
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRejectDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleReject}
              disabled={processing}
              data-testid="confirm-reject-btn"
            >
              {processing ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <XCircle className="w-4 h-4 mr-2" />
              )}
              Reject Lead
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default LeadsPage;
