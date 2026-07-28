/**
 * DemandLettersPage — management view for the bulk demand-letter workflow.
 *
 * Lets the finance/admin team:
 *   • See every demand letter that has been generated (across batches).
 *   • Filter by milestone / batch / emailed-or-not.
 *   • Trigger a fresh bulk-generation for the current milestone.
 *   • Multi-select rows and fire a bulk email send in one click.
 */
import { useEffect, useMemo, useState, useCallback } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { useAuth } from "../context/AuthContext";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Checkbox } from "../components/ui/checkbox";
import { Input } from "../components/ui/input";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "../components/ui/select";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "../components/ui/table";
import {
  Mail, RefreshCw, Loader2, FileText, CheckCircle2, AlertTriangle,
  MailWarning, Send, Eye,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const formatDate = (iso) => {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString("en-IN", {
      day: "2-digit", month: "short", year: "numeric",
      hour: "2-digit", minute: "2-digit",
    });
  } catch {
    return iso;
  }
};

const DemandLettersPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [emailing, setEmailing] = useState(false);
  const [selected, setSelected] = useState(new Set());
  const [emailedFilter, setEmailedFilter] = useState(
    searchParams.get("emailed") || "all",
  );
  const [stageFilter, setStageFilter] = useState(searchParams.get("stage_key") || "");
  const [search, setSearch] = useState("");
  const batchId = searchParams.get("batch_id") || "";
  const canEmail = ["admin", "manager", "accounts"].includes(user?.role);

  const fetchRows = useCallback(async () => {
    setRefreshing(true);
    try {
      const params = {};
      if (stageFilter) params.stage_key = stageFilter;
      if (batchId) params.batch_id = batchId;
      if (emailedFilter === "yes") params.emailed = true;
      if (emailedFilter === "no") params.emailed = false;
      const res = await axios.get(`${API}/documents/demand-letters`, { params });
      setRows(res.data?.demand_letters || []);
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Failed to load demand letters");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [stageFilter, batchId, emailedFilter]);

  useEffect(() => { fetchRows(); }, [fetchRows]);

  // Distinct stage keys sourced from the current data — plus batch scoping.
  const stageOptions = useMemo(() => {
    const map = new Map();
    rows.forEach((r) => {
      if (r.stage_key) map.set(r.stage_key, r.stage_name || r.stage_key);
    });
    return Array.from(map.entries()).map(([k, n]) => ({ key: k, name: n }));
  }, [rows]);

  const filteredRows = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) => {
      const hay =
        `${r.customer_name || ""} ${r.unit_number || ""} ${r.customer_email || ""}`.toLowerCase();
      return hay.includes(q);
    });
  }, [rows, search]);

  const visibleIds = useMemo(
    () => filteredRows.map((r) => r.id),
    [filteredRows],
  );
  const allChecked = visibleIds.length > 0 && visibleIds.every((id) => selected.has(id));
  const someChecked = !allChecked && visibleIds.some((id) => selected.has(id));

  const toggleOne = (id) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };
  const toggleAll = () => {
    setSelected((prev) => {
      const next = new Set(prev);
      const allInView = visibleIds.every((id) => next.has(id));
      if (allInView) visibleIds.forEach((id) => next.delete(id));
      else visibleIds.forEach((id) => next.add(id));
      return next;
    });
  };

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const res = await axios.post(`${API}/documents/generate-bulk-demand-letters`);
      const { generated_count, skipped_count, error_count, stage_name } = res.data;
      toast.success(
        `${stage_name}: ${generated_count} generated • ${skipped_count} already existed` +
        (error_count ? ` • ${error_count} errors` : ""),
      );
      await fetchRows();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Failed to generate");
    } finally {
      setGenerating(false);
    }
  };

  const handleEmailSelected = async () => {
    const ids = Array.from(selected);
    if (ids.length === 0) {
      toast.error("Select at least one demand letter first");
      return;
    }
    if (!window.confirm(
      `Send ${ids.length} demand letter email${ids.length === 1 ? "" : "s"} now?\n\n` +
      "Each customer will receive a PDF attachment of their letter."
    )) return;
    setEmailing(true);
    try {
      const res = await axios.post(`${API}/documents/bulk-email-demand-letters`, { ids });
      const { sent_count, failed_count } = res.data;
      if (failed_count > 0) {
        toast.warning(
          `Sent ${sent_count} • Failed ${failed_count}. Failed rows kept their previous status.`,
        );
      } else {
        toast.success(`Sent ${sent_count} demand letter${sent_count === 1 ? "" : "s"}`);
      }
      setSelected(new Set());
      await fetchRows();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Bulk email failed");
    } finally {
      setEmailing(false);
    }
  };

  const clearBatchFilter = () => {
    const p = new URLSearchParams(searchParams);
    p.delete("batch_id");
    setSearchParams(p, { replace: true });
  };

  const emailedStats = useMemo(() => {
    let sent = 0, pending = 0, failed = 0;
    for (const r of rows) {
      if (r.emailed_at) sent += 1;
      else if (r.email_status && r.email_status !== "sent") failed += 1;
      else pending += 1;
    }
    return { sent, pending, failed };
  }, [rows]);

  return (
    <div className="space-y-6" data-testid="demand-letters-page">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="font-heading text-3xl font-bold text-slate-900">
            Demand Letters
          </h1>
          <p className="text-slate-500 mt-1">
            Bulk-generate demand letters per construction milestone and email
            them out with a PDF attachment.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={fetchRows}
            disabled={refreshing}
            data-testid="refresh-demand-letters"
          >
            <RefreshCw className={`w-4 h-4 mr-1.5 ${refreshing ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          {canEmail && (
            <Button
              onClick={handleGenerate}
              disabled={generating}
              data-testid="generate-bulk-btn"
            >
              {generating ? (
                <Loader2 className="w-4 h-4 mr-1.5 animate-spin" />
              ) : (
                <FileText className="w-4 h-4 mr-1.5" />
              )}
              Generate for current stage
            </Button>
          )}
        </div>
      </div>

      {/* Summary tiles */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-3">
              <FileText className="w-8 h-8 text-blue-600" />
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-500">Total Letters</p>
                <p className="text-2xl font-bold" data-testid="stat-total">{rows.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-8 h-8 text-emerald-600" />
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-500">Emailed</p>
                <p className="text-2xl font-bold text-emerald-700" data-testid="stat-emailed">
                  {emailedStats.sent}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-3">
              <MailWarning className="w-8 h-8 text-amber-600" />
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-500">Pending</p>
                <p className="text-2xl font-bold text-amber-700" data-testid="stat-pending">
                  {emailedStats.pending}
                </p>
                {emailedStats.failed > 0 && (
                  <p className="text-xs text-red-600 mt-0.5">
                    {emailedStats.failed} failed previously
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Filter</CardTitle>
          <CardDescription>
            {batchId ? (
              <>
                Viewing batch <code className="text-xs bg-slate-100 px-1.5 py-0.5 rounded">{batchId.slice(0, 8)}…</code>{" "}
                <button
                  type="button"
                  className="underline text-slate-500 hover:text-slate-800"
                  onClick={clearBatchFilter}
                  data-testid="clear-batch-filter"
                >
                  clear
                </button>
              </>
            ) : "Filter by milestone, email status, or customer text."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <Input
                placeholder="Search customer / unit / email"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                data-testid="filter-search"
              />
            </div>
            <div>
              <Select
                value={stageFilter || "all"}
                onValueChange={(v) => setStageFilter(v === "all" ? "" : v)}
              >
                <SelectTrigger data-testid="filter-stage">
                  <SelectValue placeholder="All milestones" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All milestones</SelectItem>
                  {stageOptions.map((s) => (
                    <SelectItem key={s.key} value={s.key}>{s.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Select value={emailedFilter} onValueChange={setEmailedFilter}>
                <SelectTrigger data-testid="filter-emailed">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="yes">Emailed</SelectItem>
                  <SelectItem value="no">Not emailed</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Bulk-select toolbar */}
      {selected.size > 0 && canEmail && (
        <div
          className="flex items-center justify-between gap-3 px-4 py-2 rounded-lg border border-indigo-200 bg-indigo-50"
          data-testid="bulk-toolbar"
        >
          <div className="text-sm text-indigo-900">
            <span className="font-semibold" data-testid="bulk-selected-count">
              {selected.size} selected
            </span>
            <button
              type="button"
              className="ml-3 text-xs underline hover:text-indigo-950"
              onClick={() => setSelected(new Set())}
              data-testid="bulk-clear-selection"
            >
              Clear
            </button>
          </div>
          <Button
            onClick={handleEmailSelected}
            disabled={emailing}
            data-testid="bulk-email-btn"
          >
            {emailing ? (
              <Loader2 className="w-4 h-4 mr-1.5 animate-spin" />
            ) : (
              <Send className="w-4 h-4 mr-1.5" />
            )}
            Email Selected ({selected.size})
          </Button>
        </div>
      )}

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center h-40">
              <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
            </div>
          ) : filteredRows.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-500">
              <FileText className="w-12 h-12 mb-3 text-slate-300" />
              <p className="text-lg font-medium">No demand letters yet</p>
              <p className="text-sm">
                Click &ldquo;Generate for current stage&rdquo; to create the first batch.
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  {canEmail && (
                    <TableHead className="w-10">
                      <Checkbox
                        checked={allChecked ? true : someChecked ? "indeterminate" : false}
                        onCheckedChange={toggleAll}
                        aria-label="Select all"
                        data-testid="bulk-select-all"
                      />
                    </TableHead>
                  )}
                  <TableHead>Customer</TableHead>
                  <TableHead>Unit</TableHead>
                  <TableHead>Milestone</TableHead>
                  <TableHead>Generated</TableHead>
                  <TableHead>Emailed</TableHead>
                  <TableHead className="text-center">Preview</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredRows.map((r) => {
                  const emailed = Boolean(r.emailed_at);
                  const failed = !emailed && r.email_status && r.email_status !== "sent";
                  return (
                    <TableRow key={r.id} data-testid={`demand-row-${r.id}`}>
                      {canEmail && (
                        <TableCell className="w-10">
                          <Checkbox
                            checked={selected.has(r.id)}
                            onCheckedChange={() => toggleOne(r.id)}
                            aria-label="Select row"
                            data-testid={`select-row-${r.id}`}
                          />
                        </TableCell>
                      )}
                      <TableCell>
                        <div
                          className="cursor-pointer hover:text-primary"
                          onClick={() => r.customer_id && navigate(`/customers/${r.customer_id}`)}
                        >
                          <div className="font-medium">{r.customer_name || "—"}</div>
                          <div className="text-xs text-slate-500">{r.customer_email || "no email on file"}</div>
                        </div>
                      </TableCell>
                      <TableCell className="font-mono text-sm">
                        {r.unit_number || "—"}
                      </TableCell>
                      <TableCell>
                        {r.stage_name ? (
                          <Badge variant="secondary" className="font-normal">
                            {r.stage_name}
                          </Badge>
                        ) : (
                          <span className="text-slate-400 text-xs">no milestone tag</span>
                        )}
                      </TableCell>
                      <TableCell className="text-sm text-slate-600">
                        {formatDate(r.generated_at)}
                      </TableCell>
                      <TableCell>
                        {emailed ? (
                          <div className="flex items-center gap-1.5 text-emerald-700">
                            <CheckCircle2 className="w-4 h-4" />
                            <span className="text-xs">{formatDate(r.emailed_at)}</span>
                          </div>
                        ) : failed ? (
                          <Badge className="bg-red-100 text-red-800 border-red-200">
                            <AlertTriangle className="w-3 h-3 mr-1" />
                            {r.email_status}
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="text-slate-500">Not sent</Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-center">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => window.open(`${API}/documents/preview/${r.id}`, "_blank")}
                          data-testid={`preview-${r.id}`}
                          title="Preview / download"
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default DemandLettersPage;
