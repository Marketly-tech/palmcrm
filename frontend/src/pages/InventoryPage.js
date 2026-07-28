/**
 * InventoryPage — Flat inventory & revenue management.
 *
 * Layout: 6 KPI cards → share-type toggle → floor-wise grid → import panel.
 * Uses ``GET /api/inventory/summary`` for the KPI numbers (all six update
 * instantly when the RRL / Landowner filter toggles) and
 * ``GET /api/inventory/units`` for the grid.
 *
 * Cell colour rules (visual identity for finance at a glance):
 *   RRL     Available → light blue      Sold/Booked → dark blue
 *   Owner   Available → light emerald   Sold/Booked → dark emerald
 *   Blocked → slate
 */
import { useEffect, useMemo, useState, useCallback } from "react";
import axios from "axios";
import { toast } from "sonner";
import { useAuth } from "../context/AuthContext";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Tabs, TabsList, TabsTrigger } from "../components/ui/tabs";
import {
  Building2, RefreshCw, Upload, Loader2, TrendingUp, Wallet,
  AlertTriangle, Percent, BarChart3, IndianRupee, FileSpreadsheet,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Compact Indian rupee formatter (₹1.2 Cr / ₹34.5 L / ₹12,345).
const inr = (n) => {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  const abs = Math.abs(n);
  if (abs >= 1e7) return `₹${(n / 1e7).toFixed(2)} Cr`;
  if (abs >= 1e5) return `₹${(n / 1e5).toFixed(2)} L`;
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 }).format(n).replace(/^/, "₹");
};

// Tailwind JIT purges classes that aren't statically detectable, so map
// tones to literal class-name bundles instead of interpolating.
const toneStyles = {
  slate: { border: "border-slate-400", text: "text-slate-800", bg: "bg-slate-100", icon: "text-slate-700" },
  blue: { border: "border-blue-400", text: "text-blue-800", bg: "bg-blue-100", icon: "text-blue-700" },
  emerald: { border: "border-emerald-400", text: "text-emerald-800", bg: "bg-emerald-100", icon: "text-emerald-700" },
  red: { border: "border-red-400", text: "text-red-800", bg: "bg-red-100", icon: "text-red-700" },
  amber: { border: "border-amber-400", text: "text-amber-800", bg: "bg-amber-100", icon: "text-amber-700" },
  indigo: { border: "border-indigo-400", text: "text-indigo-800", bg: "bg-indigo-100", icon: "text-indigo-700" },
  violet: { border: "border-violet-400", text: "text-violet-800", bg: "bg-violet-100", icon: "text-violet-700" },
};

const kpiTile = ({ icon: Icon, label, value, tone = "slate", testId, subtitle }) => {
  const t = toneStyles[tone] || toneStyles.slate;
  return (
    <Card
      className={`border-l-4 ${t.border}`}
      data-testid={testId}
      key={testId}
    >
      <CardContent className="py-4">
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="text-[11px] uppercase tracking-wide text-slate-500 font-semibold">{label}</p>
            <p className={`text-2xl font-bold ${t.text} mt-1`} data-testid={`${testId}-value`}>
              {value}
            </p>
            {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
          </div>
          <div className={`rounded-lg p-2 ${t.bg}`}>
            <Icon className={`w-5 h-5 ${t.icon}`} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const cellColor = (u) => {
  // Blocked wins first — pertinent for operational holds.
  if (u.status === "BLOCKED") return "bg-slate-200 text-slate-600 border-slate-300";
  const sold = u.status === "SOLD" || u.status === "BOOKED";
  if (u.share_type === "LAND_OWNER") {
    return sold
      ? "bg-emerald-600 text-white border-emerald-700 hover:bg-emerald-700"
      : "bg-emerald-100 text-emerald-800 border-emerald-300 hover:bg-emerald-200";
  }
  // Default to RRL / builder.
  return sold
    ? "bg-blue-600 text-white border-blue-700 hover:bg-blue-700"
    : "bg-blue-100 text-blue-800 border-blue-300 hover:bg-blue-200";
};

const InventoryPage = () => {
  const { user } = useAuth();
  const canImport = user?.role === "admin";
  const [share, setShare] = useState("ALL"); // ALL | RRL | LAND_OWNER
  const [summary, setSummary] = useState(null);
  const [units, setUnits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);

  const fetchAll = useCallback(async () => {
    setRefreshing(true);
    try {
      const params = share !== "ALL" ? { share_type: share } : {};
      // Summary always filters to current toggle; unit list stays unfiltered so
      // the grid shows every unit (with a visual dimming for filtered-out ones
      // driven by ``share`` below).
      const [s, u] = await Promise.all([
        axios.get(`${API}/inventory/summary`, { params }),
        axios.get(`${API}/inventory/units`),
      ]);
      setSummary(s.data);
      setUnits(u.data?.units || []);
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Failed to load inventory");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [share]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const floors = useMemo(() => {
    const map = new Map();
    units.forEach((u) => {
      const f = u.floor || 0;
      if (!map.has(f)) map.set(f, []);
      map.get(f).push(u);
    });
    // Desc by floor for a natural tower-top-first view.
    return Array.from(map.entries()).sort((a, b) => b[0] - a[0]);
  }, [units]);

  const isDimmed = (u) =>
    share !== "ALL" && u.share_type !== share;

  const handleImport = async (file) => {
    if (!file) return;
    setImporting(true);
    setImportResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("project", "RRL PALM ALTEZZE");
      fd.append("tower", "A");
      fd.append("replace_existing", "false");
      const res = await axios.post(`${API}/units/import-file`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setImportResult(res.data);
      toast.success(
        `Imported ${res.data.created} new, ${res.data.updated} updated ` +
        (res.data.error_count ? `(${res.data.error_count} errors)` : "")
      );
      await fetchAll();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Import failed");
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="space-y-6" data-testid="inventory-page">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="font-heading text-3xl font-bold text-slate-900 flex items-center gap-2">
            <Building2 className="w-8 h-8 text-primary" /> Inventory
          </h1>
          <p className="text-slate-500 mt-1">
            Flat-wise availability, revenue projection and valuation across RRL &amp; Landowner shares.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={fetchAll}
            disabled={refreshing}
            data-testid="refresh-inventory-btn"
          >
            <RefreshCw className={`w-4 h-4 mr-1.5 ${refreshing ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Share-type filter — updates the KPIs instantly */}
      <Tabs value={share} onValueChange={setShare} className="w-full">
        <TabsList data-testid="share-tabs">
          <TabsTrigger value="ALL" data-testid="share-tab-ALL">All shares</TabsTrigger>
          <TabsTrigger value="RRL" data-testid="share-tab-RRL">RRL Share</TabsTrigger>
          <TabsTrigger value="LAND_OWNER" data-testid="share-tab-LAND_OWNER">Landowner Share</TabsTrigger>
        </TabsList>
      </Tabs>

      {/* 6 KPI cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3" data-testid="kpi-grid">
        {loading || !summary ? (
          [...Array(6)].map((_, i) => (
            <Card key={i}><CardContent className="py-6"><Loader2 className="w-5 h-5 animate-spin text-slate-300" /></CardContent></Card>
          ))
        ) : (
          <>
            {kpiTile({
              icon: TrendingUp, label: "Projected Revenue",
              value: inr(summary.total_projected_revenue), tone: "blue",
              testId: "kpi-projected",
              subtitle: `${summary.total_units} units in scope`,
            })}
            {kpiTile({
              icon: Wallet, label: "Collected",
              value: inr(summary.collected_till_date), tone: "emerald",
              testId: "kpi-collected",
              subtitle: summary.total_projected_revenue > 0
                ? `${Math.round((summary.collected_till_date / summary.total_projected_revenue) * 100)}% of projected`
                : "—",
            })}
            {kpiTile({
              icon: AlertTriangle, label: "Outstanding",
              value: inr(summary.outstanding), tone: "red",
              testId: "kpi-outstanding",
            })}
            {kpiTile({
              icon: Percent, label: "Interest",
              value: inr(summary.interest_amount), tone: "amber",
              testId: "kpi-interest",
            })}
            {kpiTile({
              icon: BarChart3, label: "Avg Sold Rate",
              value: summary.avg_sold_rate > 0 ? `₹${summary.avg_sold_rate.toLocaleString("en-IN")}/sft` : "—",
              tone: "indigo",
              testId: "kpi-avg-rate",
              subtitle: `${summary.counts_by_status?.SOLD || 0} sold units`,
            })}
            {kpiTile({
              icon: IndianRupee, label: "Total Valuation",
              value: inr(summary.total_valuation), tone: "violet",
              testId: "kpi-valuation",
              subtitle: `${summary.total_sba?.toLocaleString("en-IN")} sq ft SBA`,
            })}
          </>
        )}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600" data-testid="legend">
        <span className="font-semibold">Legend:</span>
        <span className="inline-flex items-center gap-1"><span className="w-3.5 h-3.5 rounded bg-blue-100 border border-blue-300 inline-block" /> RRL Available</span>
        <span className="inline-flex items-center gap-1"><span className="w-3.5 h-3.5 rounded bg-blue-600 border border-blue-700 inline-block" /> RRL Sold/Booked</span>
        <span className="inline-flex items-center gap-1"><span className="w-3.5 h-3.5 rounded bg-emerald-100 border border-emerald-300 inline-block" /> Landowner Available</span>
        <span className="inline-flex items-center gap-1"><span className="w-3.5 h-3.5 rounded bg-emerald-600 border border-emerald-700 inline-block" /> Landowner Sold/Booked</span>
        <span className="inline-flex items-center gap-1"><span className="w-3.5 h-3.5 rounded bg-slate-200 border border-slate-300 inline-block" /> Blocked</span>
      </div>

      {/* Floor-wise grid */}
      <Card>
        <CardHeader>
          <CardTitle>Floor-wise Availability</CardTitle>
          <CardDescription>
            {units.length} units across {floors.length} floors
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-40">
              <Loader2 className="w-6 h-6 animate-spin text-slate-300" />
            </div>
          ) : units.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              <FileSpreadsheet className="w-10 h-10 mx-auto mb-3 text-slate-300" />
              <p className="font-medium">No units yet</p>
              <p className="text-sm">Import a Flat-Details spreadsheet below to populate the grid.</p>
            </div>
          ) : (
            <div className="space-y-3" data-testid="floor-grid">
              {floors.map(([floor, list]) => (
                <div key={floor} className="flex items-center gap-3" data-testid={`floor-row-${floor}`}>
                  <div className="w-16 shrink-0 text-right text-xs uppercase tracking-wide text-slate-500 font-semibold">
                    Floor<br /><span className="text-lg text-slate-800 font-bold">{floor}</span>
                  </div>
                  <div className="flex flex-wrap gap-2 flex-1">
                    {list.map((u) => (
                      <button
                        type="button"
                        key={u.id}
                        title={`${u.unit_number} • ${u.bhk_type || "?"} • ${u.saleable_area || 0} sft • ${u.share_type || "—"} • ${u.status || "—"}`}
                        className={
                          "w-16 h-16 rounded-md border text-xs font-mono font-semibold flex flex-col items-center justify-center transition-all " +
                          cellColor(u) +
                          (isDimmed(u) ? " opacity-25" : "")
                        }
                        data-testid={`unit-cell-${u.unit_number}`}
                      >
                        <span className="text-sm">{u.unit_number}</span>
                        <span className="text-[9px] opacity-80">{u.saleable_area}</span>
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Import panel — admin only */}
      {canImport && (
        <Card data-testid="import-panel">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="w-5 h-5" /> Import Inventory
            </CardTitle>
            <CardDescription>
              Upload a Flat-Details style .xlsx (with columns
              &nbsp;<code className="text-xs bg-slate-100 px-1 py-0.5 rounded">Unit No.</code>,
              &nbsp;<code className="text-xs bg-slate-100 px-1 py-0.5 rounded">Unit Type</code>,
              &nbsp;<code className="text-xs bg-slate-100 px-1 py-0.5 rounded">S.B.A (Sq. Ft.)</code>,
              &nbsp;<code className="text-xs bg-slate-100 px-1 py-0.5 rounded">Ownership</code>,
              &nbsp;<code className="text-xs bg-slate-100 px-1 py-0.5 rounded">Sold / Unsold</code>).
              Re-uploading updates existing rows by <em>unit number</em>.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Label htmlFor="inventory-file-input" className="text-sm">Select .xlsx or .csv file</Label>
            <Input
              id="inventory-file-input"
              type="file"
              accept=".xlsx,.xls,.csv"
              onChange={(e) => handleImport(e.target.files?.[0])}
              disabled={importing}
              data-testid="inventory-file-input"
            />
            {importing && (
              <p className="text-sm text-slate-500 flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" /> Uploading…
              </p>
            )}
            {importResult && (
              <div className="text-sm text-slate-700 bg-slate-50 border rounded p-3" data-testid="import-result">
                <p>
                  <Badge className="bg-emerald-100 text-emerald-800 border-emerald-300 mr-2">
                    {importResult.created} created
                  </Badge>
                  <Badge className="bg-blue-100 text-blue-800 border-blue-300 mr-2">
                    {importResult.updated} updated
                  </Badge>
                  {importResult.error_count > 0 && (
                    <Badge className="bg-red-100 text-red-800 border-red-300">
                      {importResult.error_count} errors
                    </Badge>
                  )}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default InventoryPage;
