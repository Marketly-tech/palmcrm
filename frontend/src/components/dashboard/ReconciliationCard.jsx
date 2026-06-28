/**
 * ReconciliationCard — admin-only debug widget on the main dashboard.
 *
 * Surfaces the difference between the two revenue computations the dashboard
 * exposes (Total Revenue Collected vs Total Collected Cumulative) and lists
 * orphan transactions whose customer_id no longer exists in the customers
 * collection. Admin can hard-delete each orphan inline.
 */
import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Separator } from "../ui/separator";
import {
  AlertTriangle, CheckCircle2, RefreshCw, Trash2, Loader2,
  ShieldAlert,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const INR = (n) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(n || 0);

const verdictTheme = {
  ok: {
    border: "border-emerald-300",
    bg: "from-emerald-50 to-white",
    icon: <CheckCircle2 className="w-5 h-5 text-emerald-600" />,
    label: "Reconciled",
    labelClass: "bg-emerald-100 text-emerald-700 border-emerald-200",
  },
  orphans: {
    border: "border-amber-300",
    bg: "from-amber-50 to-white",
    icon: <ShieldAlert className="w-5 h-5 text-amber-700" />,
    label: "Drift detected",
    labelClass: "bg-amber-100 text-amber-800 border-amber-300",
  },
  unknown: {
    border: "border-rose-300",
    bg: "from-rose-50 to-white",
    icon: <AlertTriangle className="w-5 h-5 text-rose-600" />,
    label: "Unexplained drift",
    labelClass: "bg-rose-100 text-rose-700 border-rose-200",
  },
};

const ReconciliationCard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [expanded, setExpanded] = useState(false);

  const fetchReport = useCallback(async ({ silent } = { silent: false }) => {
    if (!silent) setLoading(true);
    else setRefreshing(true);
    try {
      const res = await axios.get(`${API}/dashboard/reconciliation`);
      if (res.data?.error) {
        // Non-admin or backend error — hide the widget entirely.
        setData({ unauthorised: true });
      } else {
        setData(res.data);
      }
    } catch {
      setData({ unauthorised: true });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchReport();
  }, [fetchReport]);

  const handleDeleteOrphan = async (txn) => {
    if (
      !window.confirm(
        `Delete orphan transaction ${txn.transaction_id?.slice(0, 8) || "?"} ` +
          `for ₹${(txn.amount || 0).toLocaleString("en-IN")}? This cannot be undone.`
      )
    ) {
      return;
    }
    setDeletingId(txn.transaction_id);
    try {
      await axios.post(
        `${API}/dashboard/reconciliation/delete-orphan/${txn.transaction_id}`
      );
      toast.success(`Removed orphan transaction (${INR(txn.amount)})`);
      fetchReport({ silent: true });
    } catch (e) {
      // Backend returns {error: '...'} for admin-block / customer-still-exists,
      // and {detail: '...'} for FastAPI HTTPException. Cover both.
      const reason =
        e?.response?.data?.error || e?.response?.data?.detail || "Failed to delete orphan";
      toast.error(reason);
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return (
      <Card className="border-slate-200">
        <CardContent className="py-6 flex items-center justify-center text-slate-500 text-sm">
          <Loader2 className="w-4 h-4 animate-spin mr-2" />
          Reconciling revenue numbers…
        </CardContent>
      </Card>
    );
  }

  if (!data || data.unauthorised) return null;

  const theme = verdictTheme[data.verdict] || verdictTheme.unknown;
  const totalOrphans = data.orphan_count || 0;
  const visibleOrphans = expanded
    ? data.orphan_samples
    : data.orphan_samples?.slice(0, 5);

  return (
    <Card
      className={`bg-gradient-to-br ${theme.bg} ${theme.border} shadow-sm`}
      data-testid="reconciliation-card"
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className="mt-0.5">{theme.icon}</div>
            <div>
              <CardTitle className="text-base text-slate-900">
                Revenue Reconciliation
              </CardTitle>
              <CardDescription className="text-slate-600">
                {data.message}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge
              variant="outline"
              className={`${theme.labelClass} text-xs`}
              data-testid="reconciliation-verdict"
            >
              {theme.label}
            </Badge>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => fetchReport({ silent: true })}
              disabled={refreshing}
              data-testid="reconciliation-refresh-btn"
              aria-label="Refresh reconciliation report"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Side-by-side comparison */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="rounded-lg border bg-white p-3" data-testid="rec-aggregation">
            <div className="text-xs uppercase tracking-wide text-slate-500 font-semibold mb-1">
              Total Revenue Collected
            </div>
            <div className="text-xl font-bold text-slate-900 font-mono">
              {INR(data.aggregation_total)}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              ∑ amount across {data.aggregation_count} txns (all rows)
            </div>
          </div>

          <div className="rounded-lg border bg-white p-3" data-testid="rec-loop">
            <div className="text-xs uppercase tracking-wide text-slate-500 font-semibold mb-1">
              Total Collected (Cumulative)
            </div>
            <div className="text-xl font-bold text-slate-900 font-mono">
              {INR(data.loop_total)}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              ∑ per known customer ({data.loop_count} txns)
            </div>
          </div>

          <div
            className={`rounded-lg border p-3 ${
              Math.abs(data.difference) > 0.5
                ? "border-rose-300 bg-rose-50"
                : "border-emerald-300 bg-emerald-50"
            }`}
            data-testid="rec-difference"
          >
            <div className="text-xs uppercase tracking-wide font-semibold mb-1 text-slate-700">
              Difference
            </div>
            <div
              className={`text-xl font-bold font-mono ${
                Math.abs(data.difference) > 0.5 ? "text-rose-700" : "text-emerald-700"
              }`}
            >
              {INR(data.difference)}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              Orphan txns: {totalOrphans} · {INR(data.orphan_total)}
            </div>
          </div>
        </div>

        {/* Orphan list */}
        {totalOrphans > 0 && (
          <>
            <Separator />
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-semibold text-slate-800">
                  Orphan transactions (customer no longer exists)
                </div>
                {totalOrphans > 5 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setExpanded((e) => !e)}
                    className="h-7 text-xs"
                    data-testid="reconciliation-expand-btn"
                  >
                    {expanded ? "Show less" : `Show all ${data.orphan_samples?.length || 0}`}
                  </Button>
                )}
              </div>
              <div className="border rounded-lg bg-white overflow-hidden" data-testid="reconciliation-orphan-list">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                      <th className="text-left px-3 py-2 font-semibold">Date</th>
                      <th className="text-left px-3 py-2 font-semibold">Type</th>
                      <th className="text-left px-3 py-2 font-semibold">Receipt</th>
                      <th className="text-left px-3 py-2 font-semibold">Customer ID</th>
                      <th className="text-right px-3 py-2 font-semibold">Amount</th>
                      <th className="text-right px-3 py-2 font-semibold">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {visibleOrphans?.map((o) => (
                      <tr
                        key={o.transaction_id}
                        className="border-t hover:bg-slate-50"
                        data-testid={`orphan-row-${o.transaction_id}`}
                      >
                        <td className="px-3 py-2 text-xs text-slate-700">
                          {o.transaction_date || "—"}
                        </td>
                        <td className="px-3 py-2 text-xs">
                          <Badge variant="outline" className="text-[10px]">
                            {o.transaction_type || "—"}
                          </Badge>
                        </td>
                        <td className="px-3 py-2 text-xs text-slate-700">
                          {o.receipt_number || "—"}
                        </td>
                        <td className="px-3 py-2 text-xs font-mono text-slate-500">
                          {(o.customer_id || "—").slice(0, 8)}…
                        </td>
                        <td className="px-3 py-2 text-right font-mono font-medium text-slate-900">
                          {INR(o.amount)}
                        </td>
                        <td className="px-3 py-2 text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteOrphan(o)}
                            disabled={deletingId === o.transaction_id}
                            className="h-7 text-rose-600 hover:bg-rose-50"
                            data-testid={`orphan-delete-${o.transaction_id}`}
                            aria-label="Delete orphan transaction"
                          >
                            {deletingId === o.transaction_id ? (
                              <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            ) : (
                              <Trash2 className="w-3.5 h-3.5" />
                            )}
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {data.orphan_count > (data.orphan_samples?.length || 0) && (
                <div className="text-xs text-slate-500 mt-2">
                  Showing {data.orphan_samples?.length} of {data.orphan_count} orphans
                  (capped at 25 per refresh). Delete some and refresh to see more.
                </div>
              )}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default ReconciliationCard;
