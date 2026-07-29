/**
 * ConstructionUpdateDialog — one-click bulk construction-update mailer.
 *
 * Flow (in a single dialog, no page changes):
 *   1. Compose  — admin enters Drive link + slab/stage name + optional filter.
 *   2. Preview  — hit "Preview & Edit"; the backend renders the FIRST
 *      recipient's email so the admin can visually confirm the personalisation.
 *      Subject + HTML body are then editable (so admins can tweak the
 *      auto-generated template before firing).
 *   3. Send     — final confirm & fire via
 *      ``POST /api/customers/construction-update/send``.
 *
 * Persistence is intentionally light — every send lands in
 * ``communication_logs`` and no separate campaigns table is kept.
 */
import { useState, useMemo, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";
import { Badge } from "../ui/badge";
import { Separator } from "../ui/separator";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription,
  DialogFooter, DialogTrigger,
} from "../ui/dialog";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "../ui/select";
import {
  Send, Loader2, Eye, ArrowLeft, Megaphone, Info, Link as LinkIcon,
  Mail, Users,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Known payment stages — kept here (not fetched) so the dropdown is instant.
// If the user picks "Custom" they can still type any slab name in the input.
const STAGE_PRESETS = [
  "Foundation Slab",
  "Podium Slab",
  "2nd Floor Roof Slab",
  "6th Floor Roof Slab",
  "10th Floor Roof Slab",
  "14th Floor Roof Slab",
  "18th Floor Roof Slab",
  "22nd Floor Roof Slab",
  "Top Roof Slab",
  "Flooring Complete",
  "Handover / Possession",
];

const TOWER_PRESETS = ["A", "B", "C"];

const CUSTOMER_STAGE_PRESETS = [
  { key: "", label: "All active customers" },
  { key: "booking_confirmed", label: "Booking confirmed" },
  { key: "agreement_signed", label: "Agreement signed" },
  { key: "under_construction", label: "Under construction" },
  { key: "possession_ready", label: "Possession ready" },
];

const ConstructionUpdateDialog = ({
  trigger,
  defaultStageName = "",
  onDone,
  testId = "construction-update-dialog",
}) => {
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState("compose"); // compose | preview
  const [driveLink, setDriveLink] = useState("");
  const [stageName, setStageName] = useState(defaultStageName);
  const [customerFilter, setCustomerFilter] = useState("");
  const [towerFilter, setTowerFilter] = useState("");
  const [subject, setSubject] = useState("");
  const [bodyHtml, setBodyHtml] = useState("");
  const [preview, setPreview] = useState(null); // {recipient_count, has_email_count, preview:{...}, subject_template, body_html_template}
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [sending, setSending] = useState(false);

  useEffect(() => { if (!open) { setStep("compose"); setPreview(null); } }, [open]);
  useEffect(() => {
    if (defaultStageName && !stageName) setStageName(defaultStageName);
  }, [defaultStageName, stageName]);

  const filterPayload = useMemo(() => {
    const f = {};
    if (customerFilter) f.current_stage = customerFilter;
    if (towerFilter) f.tower = towerFilter;
    return f;
  }, [customerFilter, towerFilter]);

  const handlePreview = async () => {
    if (!driveLink.trim() || !stageName.trim()) {
      toast.error("Drive link and slab name are both required");
      return;
    }
    setLoadingPreview(true);
    try {
      const res = await axios.post(
        `${API}/customers/construction-update/preview`,
        {
          drive_link: driveLink.trim(),
          stage_name: stageName.trim(),
          filter: filterPayload,
        },
      );
      const p = res.data;
      setPreview(p);
      // Seed editable subject / body from the backend's template on first
      // preview only. If the admin later re-previews they keep their edits.
      if (!subject) setSubject(p.subject_template);
      if (!bodyHtml) setBodyHtml(p.body_html_template);
      setStep("preview");
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Preview failed");
    } finally {
      setLoadingPreview(false);
    }
  };

  const handleRefreshPreview = async () => {
    // User edited subject/body → re-fetch first-customer render with their
    // custom templates so the sample re-renders live.
    if (!driveLink || !stageName) return;
    setLoadingPreview(true);
    try {
      const res = await axios.post(
        `${API}/customers/construction-update/preview`,
        {
          drive_link: driveLink.trim(),
          stage_name: stageName.trim(),
          filter: filterPayload,
          subject: subject || undefined,
          body_html: bodyHtml || undefined,
        },
      );
      setPreview(res.data);
      toast.success("Preview refreshed");
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Preview refresh failed");
    } finally {
      setLoadingPreview(false);
    }
  };

  const handleSend = async () => {
    if (!preview) return;
    const cnt = preview.has_email_count || 0;
    if (cnt === 0) {
      toast.error("No customer in scope has an email on file");
      return;
    }
    if (!window.confirm(
      `Send this construction update to ${cnt} customer${cnt === 1 ? "" : "s"}?\n\n` +
      "This will fire immediately and cannot be undone."
    )) return;
    setSending(true);
    try {
      const res = await axios.post(
        `${API}/customers/construction-update/send`,
        {
          drive_link: driveLink.trim(),
          stage_name: stageName.trim(),
          subject,
          body_html: bodyHtml,
          filter: filterPayload,
        },
      );
      const { sent_count, failed_count, skipped_no_email } = res.data;
      if (failed_count > 0 || skipped_no_email > 0) {
        toast.warning(
          `Sent ${sent_count} • Failed ${failed_count}` +
          (skipped_no_email ? ` • ${skipped_no_email} had no email` : "")
        );
      } else {
        toast.success(`Sent to ${sent_count} customer${sent_count === 1 ? "" : "s"}`);
      }
      setOpen(false);
      onDone?.(res.data);
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Send failed");
    } finally {
      setSending(false);
    }
  };

  const placeholderTip = (
    <p className="text-xs text-slate-500">
      Placeholders you can use: {" "}
      {["customer_name", "unit_number", "project", "tower", "stage_name", "drive_link"].map((p) => (
        <code key={p} className="mx-0.5 px-1 py-0.5 bg-slate-100 rounded text-[10px]">
          {`{${p}}`}
        </code>
      ))}
    </p>
  );

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="outline" data-testid={`${testId}-open`}>
            <Megaphone className="w-4 h-4 mr-1.5" />
            Send Construction Update
          </Button>
        )}
      </DialogTrigger>
      <DialogContent
        className="max-w-4xl max-h-[90vh] overflow-y-auto pr-12"
        data-testid={testId}
      >
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Megaphone className="w-5 h-5 text-primary" />
            {step === "compose" ? "Compose Construction Update" : "Preview & Edit"}
          </DialogTitle>
          <DialogDescription>
            {step === "compose"
              ? "Send a stage-wise update to all customers with a Google Drive link to the latest site photos / videos."
              : "Sample rendering for the first recipient. Edit the subject or body freely — placeholders re-render live."}
          </DialogDescription>
        </DialogHeader>

        {step === "compose" ? (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="drive-link" className="flex items-center gap-1.5">
                <LinkIcon className="w-3.5 h-3.5" /> Google Drive link *
              </Label>
              <Input
                id="drive-link"
                placeholder="https://drive.google.com/drive/folders/..."
                value={driveLink}
                onChange={(e) => setDriveLink(e.target.value)}
                data-testid="cu-drive-link"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="slab-name">Slab / Milestone name *</Label>
              <div className="flex gap-2">
                <Input
                  id="slab-name"
                  placeholder="e.g. Podium Slab, 10th Floor Roof Slab"
                  value={stageName}
                  onChange={(e) => setStageName(e.target.value)}
                  data-testid="cu-stage-name"
                  className="flex-1"
                />
                <Select onValueChange={(v) => setStageName(v)}>
                  <SelectTrigger className="w-48" data-testid="cu-stage-preset">
                    <SelectValue placeholder="Preset stages" />
                  </SelectTrigger>
                  <SelectContent>
                    {STAGE_PRESETS.map((s) => (
                      <SelectItem key={s} value={s}>{s}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Separator />

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label className="flex items-center gap-1.5">
                  <Users className="w-3.5 h-3.5" /> Customer scope
                </Label>
                <Select value={customerFilter || "all"} onValueChange={(v) => setCustomerFilter(v === "all" ? "" : v)}>
                  <SelectTrigger data-testid="cu-customer-filter">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {CUSTOMER_STAGE_PRESETS.map((s) => (
                      <SelectItem key={s.key || "all"} value={s.key || "all"}>{s.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Tower filter (optional)</Label>
                <Select value={towerFilter || "all"} onValueChange={(v) => setTowerFilter(v === "all" ? "" : v)}>
                  <SelectTrigger data-testid="cu-tower-filter">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All towers</SelectItem>
                    {TOWER_PRESETS.map((t) => (
                      <SelectItem key={t} value={t}>Tower {t}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="text-xs text-slate-500 flex items-start gap-1.5 bg-slate-50 border rounded p-2">
              <Info className="w-3.5 h-3.5 mt-0.5 shrink-0" />
              We&rsquo;ll generate a branded email using your Drive link &amp; slab
              name. You&rsquo;ll be able to edit the subject and body on the next
              screen before firing.
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Scope + counts summary */}
            <div className="flex items-center gap-2 flex-wrap" data-testid="cu-summary">
              <Badge className="bg-blue-100 text-blue-800 border-blue-200">
                <Users className="w-3 h-3 mr-1" /> {preview?.recipient_count || 0} in scope
              </Badge>
              <Badge className="bg-emerald-100 text-emerald-800 border-emerald-200">
                <Mail className="w-3 h-3 mr-1" /> {preview?.has_email_count || 0} with email
              </Badge>
              {preview?.no_email_count > 0 && (
                <Badge className="bg-amber-100 text-amber-800 border-amber-200">
                  {preview.no_email_count} skipped (no email)
                </Badge>
              )}
            </div>

            <Separator />

            {/* Editable subject + body */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div className="space-y-3">
                <div>
                  <Label className="text-xs uppercase tracking-wide text-slate-500">Subject *</Label>
                  <Input
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    className="mt-1"
                    data-testid="cu-subject"
                  />
                </div>
                <div>
                  <Label className="text-xs uppercase tracking-wide text-slate-500">HTML body *</Label>
                  <Textarea
                    value={bodyHtml}
                    onChange={(e) => setBodyHtml(e.target.value)}
                    rows={16}
                    className="mt-1 font-mono text-xs"
                    data-testid="cu-body-html"
                  />
                </div>
                {placeholderTip}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRefreshPreview}
                  disabled={loadingPreview}
                  data-testid="cu-refresh-preview"
                >
                  {loadingPreview ? (
                    <Loader2 className="w-4 h-4 mr-1.5 animate-spin" />
                  ) : (
                    <Eye className="w-4 h-4 mr-1.5" />
                  )}
                  Re-render preview with my edits
                </Button>
              </div>

              {/* Rendered sample */}
              <div className="space-y-2">
                <Label className="text-xs uppercase tracking-wide text-slate-500">
                  Sample for {preview?.preview?.customer_name || "first recipient"} &nbsp;
                  <span className="text-slate-400 normal-case font-normal">
                    &lt;{preview?.preview?.recipient_email || "—"}&gt;
                  </span>
                </Label>
                <div
                  className="bg-white border rounded p-3 text-sm"
                  data-testid="cu-preview-subject"
                >
                  <span className="text-slate-500 text-xs mr-1">Subject:</span>
                  <span className="font-semibold">{preview?.preview?.subject}</span>
                </div>
                <div
                  className="bg-white border rounded overflow-hidden"
                  style={{ maxHeight: "460px", overflowY: "auto" }}
                  data-testid="cu-preview-body"
                  dangerouslySetInnerHTML={{ __html: preview?.preview?.body_html || "" }}
                />
              </div>
            </div>
          </div>
        )}

        <DialogFooter>
          {step === "compose" ? (
            <>
              <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
              <Button
                onClick={handlePreview}
                disabled={loadingPreview || !driveLink.trim() || !stageName.trim()}
                data-testid="cu-preview-btn"
              >
                {loadingPreview ? (
                  <Loader2 className="w-4 h-4 mr-1.5 animate-spin" />
                ) : (
                  <Eye className="w-4 h-4 mr-1.5" />
                )}
                Preview &amp; Edit
              </Button>
            </>
          ) : (
            <>
              <Button
                variant="outline"
                onClick={() => setStep("compose")}
                disabled={sending}
                data-testid="cu-back"
              >
                <ArrowLeft className="w-4 h-4 mr-1.5" /> Back
              </Button>
              <Button
                onClick={handleSend}
                disabled={sending || !preview?.has_email_count}
                data-testid="cu-send-btn"
              >
                {sending ? (
                  <Loader2 className="w-4 h-4 mr-1.5 animate-spin" />
                ) : (
                  <Send className="w-4 h-4 mr-1.5" />
                )}
                Send to {preview?.has_email_count || 0} customer{(preview?.has_email_count || 0) === 1 ? "" : "s"}
              </Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ConstructionUpdateDialog;
