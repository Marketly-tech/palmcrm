/**
 * DisbursementSummaryCard — admin-only. Shows per-bank loan disbursement
 * status on the main dashboard.
 *
 * Data source: GET /api/dashboard/disbursement-summary. The card headlines
 * the "Grand Total Pending Disbursement" so an admin instantly sees how
 * much bank loan money is still outstanding, backed by a per-bank
 * breakdown. Orphan disbursement transactions (customer_id no longer in
 * customers collection) are shown in a separate "Unmatched" section with a
 * per-row delete button that calls the shared orphan-cleanup endpoint.
 */
import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Separator } from "../ui/separator";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "../ui/table";
import {
  Landmark, RefreshCw, Trash2, Loader2, AlertTriangle,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const INR = (n) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(n || 0);

const DisbursementSummaryCard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  const fetchSummary = useCallback(async () => {
    setRefreshing(true);
    try {
      const res = await axios.get(`${API}/dashboard/disbursement-summary`);
      setData(res.data);
    } catch (e) {
      toast.error(e?.response?.data?.error || "Failed to load disbursement summary");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { fetchSummary(); }, [fetchSummary]);

  const handleDeleteOrphan = async (txn) => {
    if (!window.confirm(
      `Delete unmatched disbursement of ${INR(txn.amount)} (${txn.bank_name || "no bank"})?\n\n` +
      "Customer no longer exists. This action cannot be undone."
    )) return;
    setDeletingId(txn.transaction_id);
    try {
      const res = await axios.post(
        `${API}/dashboard/reconciliation/delete-orphan/${txn.transaction_id}`,
      );
      if (res.data?.error) throw new Error(res.data.error);
      toast.success("Unmatched disbursement deleted");
      await fetchSummary();
    } catch (e) {
      toast.error(e?.response?.data?.error || e.message || "Failed to delete");
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return (
      <Card data-testid="disbursement-summary-card">
        <CardContent className="flex items-center justify-center h-40">
          <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
        </CardContent>
      </Card>
    );
  }

  if (!data || data.error) {
    return (
      <Card data-testid="disbursement-summary-card">
        <CardContent className="py-6 text-sm text-slate-500">
          {data?.error || "Disbursement summary unavailable"}
        </CardContent>
      </Card>
    );
  }

  const banks = data.banks || [];
  const hasUnmatched = (data.unmatched_count || 0) > 0;

  return (
    <Card
      className="border-indigo-200 bg-gradient-to-br from-indigo-50 to-white"
      data-testid="disbursement-summary-card"
    >
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="rounded-lg bg-indigo-100 p-2">
            <Landmark className="w-5 h-5 text-indigo-700" />
          </div>
          <div>
            <CardTitle className="text-slate-900">Bank Disbursement Summary</CardTitle>
            <CardDescription>
              Per-bank loan disbursement status across financed customers
              ({banks.reduce((a, b) => a + (b.customer_count || 0), 0)} loans tracked).
            </CardDescription>
          </div>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={fetchSummary}
          disabled={refreshing}
          data-testid="refresh-disbursement-btn"
        >
          <RefreshCw className={`w-4 h-4 mr-1.5 ${refreshing ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Headline pending amount */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2 rounded-xl border border-indigo-200 bg-white p-5">
            <p className="text-xs uppercase tracking-wider text-indigo-700 font-semibold">
              Grand Total Pending Disbursement
            </p>
            <p
              className="text-4xl md:text-5xl font-bold text-indigo-900 mt-1 tracking-tight"
              data-testid="grand-total-pending"
            >
              {INR(data.grand_total_pending)}
            </p>
            <p className="text-xs text-slate-500 mt-2">
              across {banks.length} bank{banks.length === 1 ? "" : "s"} • total
              sanctioned {INR(data.grand_total_loan)}
            </p>
          </div>
          <div className="rounded-xl border border-emerald-200 bg-white p-5">
            <p className="text-xs uppercase tracking-wider text-emerald-700 font-semibold">
              Total Disbursed To Date
            </p>
            <p
              className="text-2xl md:text-3xl font-bold text-emerald-800 mt-1 tracking-tight"
              data-testid="grand-total-disbursed"
            >
              {INR(data.grand_total_disbursed)}
            </p>
            <p className="text-xs text-slate-500 mt-2">
              Sum of every &ldquo;scheduled_disbursement&rdquo; payment logged
            </p>
          </div>
        </div>

        {/* Per-bank breakdown */}
        {banks.length > 0 ? (
          <div className="rounded-lg border bg-white overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="bg-slate-50">
                  <TableHead className="w-[35%]">Bank</TableHead>
                  <TableHead className="text-center">Loans</TableHead>
                  <TableHead className="text-right">Sanctioned</TableHead>
                  <TableHead className="text-right">Disbursed</TableHead>
                  <TableHead className="text-right">Pending</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {banks.map((b) => {
                  const pct = b.loan_amount
                    ? Math.min(100, Math.round((b.total_disbursed / b.loan_amount) * 100))
                    : 0;
                  return (
                    <TableRow
                      key={b.bank}
                      data-testid={`disbursement-row-${b.bank}`}
                    >
                      <TableCell className="font-semibold text-slate-800">
                        {b.bank}
                        {b.loan_amount > 0 && (
                          <div className="text-xs text-slate-400 font-normal mt-0.5">
                            {pct}% disbursed
                          </div>
                        )}
                      </TableCell>
                      <TableCell className="text-center text-slate-700">
                        {b.customer_count}
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm text-slate-700">
                        {b.loan_amount > 0 ? INR(b.loan_amount) : "—"}
                      </TableCell>
                      <TableCell className="text-right font-mono text-sm text-emerald-700">
                        {INR(b.total_disbursed)}
                      </TableCell>
                      <TableCell
                        className={`text-right font-mono text-sm font-semibold ${
                          b.pending_disbursement > 0 ? "text-indigo-700" : "text-slate-400"
                        }`}
                      >
                        {INR(b.pending_disbursement)}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        ) : (
          <p className="text-sm text-slate-500 italic">
            No financed customers yet — add loan details to a customer's Finance
            section to start tracking.
          </p>
        )}

        {/* Unmatched disbursements */}
        {hasUnmatched && (
          <>
            <Separator />
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  <p className="font-semibold text-slate-800">
                    Unmatched Disbursements
                  </p>
                  <Badge className="bg-amber-100 text-amber-800 border-amber-300">
                    {data.unmatched_count} • {INR(data.unmatched_total)}
                  </Badge>
                </div>
                <p className="text-xs text-slate-500">
                  Excluded from grand total • customer no longer exists
                </p>
              </div>
              <div className="rounded-lg border bg-white overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-amber-50/60">
                      <TableHead>Date</TableHead>
                      <TableHead>Bank</TableHead>
                      <TableHead>Txn Ref</TableHead>
                      <TableHead className="text-right">Amount</TableHead>
                      <TableHead className="w-16 text-center">Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.unmatched.map((t) => (
                      <TableRow
                        key={t.transaction_id}
                        data-testid={`unmatched-row-${t.transaction_id}`}
                      >
                        <TableCell className="text-sm text-slate-600 font-mono">
                          {t.transaction_date || "—"}
                        </TableCell>
                        <TableCell className="text-sm text-slate-700">
                          {t.bank_name || "—"}
                        </TableCell>
                        <TableCell
                          className="text-xs text-slate-500 font-mono truncate max-w-xs"
                          title={t.transaction_number}
                        >
                          {t.transaction_number || "—"}
                        </TableCell>
                        <TableCell className="text-right font-mono text-sm text-slate-800">
                          {INR(t.amount)}
                        </TableCell>
                        <TableCell className="text-center">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteOrphan(t)}
                            disabled={deletingId === t.transaction_id}
                            data-testid={`delete-unmatched-${t.transaction_id}`}
                            title="Delete this unmatched disbursement"
                          >
                            {deletingId === t.transaction_id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Trash2 className="w-4 h-4" />
                            )}
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default DisbursementSummaryCard;
