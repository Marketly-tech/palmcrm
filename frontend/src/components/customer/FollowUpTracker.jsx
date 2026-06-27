/**
 * FollowUpTracker - Multi-level Calling / Follow-up Tracker tied to disbursement stages.
 *
 * Behaviour
 * ─────────
 *  • Lists payment/disbursement stages where the customer is currently overdue
 *    (cumulative expected > total received). Sales/Accounts can log follow-up
 *    calls against each overdue stage.
 *  • Each entry captures: stage, call status (Dialed/Connected/Unanswered/
 *    Follow-up/Completed), free-text notes, and an optional next follow-up
 *    date/time.
 *  • UI lives inside the Notes tab with an amber palette to differentiate it
 *    from the slate-coloured notes section.
 *  • Plays a short Web-Audio chime + browser notification when a follow-up
 *    entry is logged. Reminder-time chimes are handled separately by
 *    `useFollowUpReminders` (mounted at the layout level).
 *
 * Accessible to all roles per product spec (no role gating).
 */
import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Badge } from "../ui/badge";
import { Separator } from "../ui/separator";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "../ui/select";
import {
  PhoneCall, Loader2, Plus, Trash2, AlertTriangle, Bell, CalendarClock,
} from "lucide-react";
import { playFollowUpChime } from "../../utils/followUpSound";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const STATUS_COLORS = {
  Dialed: "bg-blue-100 text-blue-700 border-blue-200",
  Connected: "bg-emerald-100 text-emerald-700 border-emerald-200",
  Unanswered: "bg-rose-100 text-rose-700 border-rose-200",
  "Follow-up": "bg-amber-100 text-amber-700 border-amber-200",
  Completed: "bg-violet-100 text-violet-700 border-violet-200",
};

const FollowUpTracker = ({ customerId }) => {
  const [data, setData] = useState({
    follow_ups: [],
    overdue_stages: [],
    all_stages: [],
    statuses: [],
    current_stage: null,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Form state
  const [stageKey, setStageKey] = useState("");
  const [status, setStatus] = useState("");
  const [notes, setNotes] = useState("");
  const [nextDate, setNextDate] = useState("");
  const [nextTime, setNextTime] = useState("");

  const fetchFollowUps = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/customers/${customerId}/follow-ups`);
      setData(res.data);
      // Default the stage selector to the first overdue stage when present.
      if (!stageKey && res.data.overdue_stages?.length > 0) {
        setStageKey(res.data.overdue_stages[0].key);
      }
    } catch {
      toast.error("Failed to load follow-up log");
    } finally {
      setLoading(false);
    }
  }, [customerId]);

  useEffect(() => {
    fetchFollowUps();
  }, [fetchFollowUps]);

  const handleSave = async () => {
    if (!stageKey || !status) {
      toast.error("Please select a stage and call status");
      return;
    }
    setSaving(true);
    try {
      await axios.post(`${API}/customers/${customerId}/follow-ups`, {
        stage_key: stageKey,
        status,
        notes,
        next_follow_up_date: nextDate || null,
        next_follow_up_time: nextTime || null,
      });
      // Audio confirmation per spec
      playFollowUpChime();
      // Best-effort browser notification (only when granted)
      if (typeof Notification !== "undefined" && Notification.permission === "granted") {
        new Notification("Follow-up logged", {
          body: `${status} • ${data.all_stages.find((s) => s.key === stageKey)?.name || ""}`,
        });
      }
      toast.success("Follow-up logged");
      setNotes("");
      setStatus("");
      setNextDate("");
      setNextTime("");
      await fetchFollowUps();
    } catch (e) {
      toast.error(e?.response?.data?.detail || "Failed to log follow-up");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this follow-up entry?")) return;
    try {
      await axios.delete(`${API}/customers/${customerId}/follow-ups/${id}`);
      toast.success("Follow-up deleted");
      await fetchFollowUps();
    } catch {
      toast.error("Failed to delete follow-up");
    }
  };

  // Group follow-ups by stage for clearer multi-level display
  const groupedByStage = data.follow_ups.reduce((acc, fu) => {
    const key = fu.stage_key || "_other";
    if (!acc[key]) acc[key] = [];
    acc[key].push(fu);
    return acc;
  }, {});

  const overdueKeys = new Set(data.overdue_stages.map((s) => s.key));
  // Allow logging against any stage (overdue or otherwise) — but surface
  // overdue ones at the top of the dropdown.
  const stageOptions = [
    ...data.overdue_stages.map((s) => ({ ...s, overdue: true })),
    ...data.all_stages
      .filter((s) => !overdueKeys.has(s.key))
      .map((s) => ({ ...s, overdue: false })),
  ];

  if (loading) {
    return (
      <Card className="border-amber-200 bg-amber-50/40">
        <CardContent className="py-8 flex items-center justify-center text-amber-700">
          <Loader2 className="w-5 h-5 animate-spin mr-2" />
          Loading follow-up tracker...
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      className="border-amber-300 bg-gradient-to-br from-amber-50 to-orange-50 shadow-sm"
      data-testid="follow-up-tracker"
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardTitle className="flex items-center gap-2 text-amber-900">
              <PhoneCall className="w-5 h-5 text-amber-700" />
              Calling & Follow-up Tracker
            </CardTitle>
            <CardDescription className="text-amber-800/80">
              Multi-level call log tied to disbursement stages. Log each
              outreach, set a next follow-up, and the CRM will chime when
              it&apos;s due.
            </CardDescription>
          </div>
          {data.overdue_stages.length > 0 && (
            <Badge
              variant="outline"
              className="border-amber-400 bg-amber-100 text-amber-900 whitespace-nowrap"
              data-testid="overdue-stage-count"
            >
              <AlertTriangle className="w-3 h-3 mr-1" />
              {data.overdue_stages.length} overdue stage
              {data.overdue_stages.length === 1 ? "" : "s"}
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        {/* Overdue stages snapshot */}
        {data.overdue_stages.length > 0 ? (
          <div className="rounded-lg border border-amber-300 bg-white/70 p-3">
            <div className="text-xs font-semibold uppercase tracking-wide text-amber-800 mb-2">
              Currently Overdue (chronological)
            </div>
            <div className="flex flex-wrap gap-2">
              {data.overdue_stages.map((s) => (
                <Badge
                  key={s.key}
                  className="bg-rose-100 text-rose-700 border border-rose-200 font-normal"
                >
                  {s.name} · {s.cumulative}%
                </Badge>
              ))}
            </div>
          </div>
        ) : (
          <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">
            No overdue stages right now. You can still log proactive
            follow-ups for any stage below.
          </div>
        )}

        {/* New entry form */}
        <div className="rounded-lg border border-amber-300 bg-white p-4 space-y-3">
          <div className="text-sm font-semibold text-amber-900 flex items-center gap-2">
            <Plus className="w-4 h-4" /> Log a new follow-up
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label className="text-xs text-slate-600">
                Disbursement Stage
              </Label>
              <Select value={stageKey} onValueChange={setStageKey}>
                <SelectTrigger data-testid="follow-up-stage-select">
                  <SelectValue placeholder="Select stage" />
                </SelectTrigger>
                <SelectContent>
                  {stageOptions.map((s) => (
                    <SelectItem key={s.key} value={s.key}>
                      {s.overdue ? "🔴 " : ""}
                      {s.name} ({s.cumulative}%)
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1">
              <Label className="text-xs text-slate-600">Call Status</Label>
              <Select value={status} onValueChange={setStatus}>
                <SelectTrigger data-testid="follow-up-status-select">
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  {(data.statuses || []).map((s) => (
                    <SelectItem key={s} value={s}>
                      {s}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1">
              <Label className="text-xs text-slate-600">
                Next Follow-up Date
              </Label>
              <Input
                type="date"
                value={nextDate}
                onChange={(e) => setNextDate(e.target.value)}
                data-testid="follow-up-next-date"
              />
            </div>

            <div className="space-y-1">
              <Label className="text-xs text-slate-600">
                Next Follow-up Time
              </Label>
              <Input
                type="time"
                value={nextTime}
                onChange={(e) => setNextTime(e.target.value)}
                data-testid="follow-up-next-time"
              />
            </div>
          </div>

          <div className="space-y-1">
            <Label className="text-xs text-slate-600">Notes</Label>
            <Textarea
              placeholder="What did the customer say? Any commitments?"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={2}
              data-testid="follow-up-notes-input"
            />
          </div>

          <div className="flex justify-end">
            <Button
              onClick={handleSave}
              disabled={saving}
              className="bg-amber-600 hover:bg-amber-700"
              data-testid="follow-up-save-btn"
            >
              {saving ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" /> Saving
                </>
              ) : (
                <>
                  <Bell className="w-4 h-4 mr-2" /> Log Follow-up
                </>
              )}
            </Button>
          </div>
        </div>

        <Separator className="bg-amber-200" />

        {/* History grouped by stage */}
        {data.follow_ups.length === 0 ? (
          <div className="text-center py-6 text-amber-800/70 text-sm">
            No follow-ups yet. Use the form above to log the first call.
          </div>
        ) : (
          <div className="space-y-4" data-testid="follow-up-history">
            {Object.entries(groupedByStage).map(([key, items]) => {
              const stage = data.all_stages.find((s) => s.key === key);
              const isOverdue = overdueKeys.has(key);
              return (
                <div
                  key={key}
                  className={`rounded-lg border p-3 ${
                    isOverdue
                      ? "border-rose-300 bg-rose-50/50"
                      : "border-amber-200 bg-white/60"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-sm font-semibold text-slate-800">
                      {stage?.name || key}
                      {stage && (
                        <span className="text-xs text-slate-500 ml-2">
                          ({stage.cumulative}%)
                        </span>
                      )}
                    </div>
                    {isOverdue && (
                      <Badge className="bg-rose-100 text-rose-700 border border-rose-200">
                        Overdue
                      </Badge>
                    )}
                  </div>
                  <div className="space-y-2">
                    {items
                      .sort((a, b) =>
                        (b.created_at || "").localeCompare(a.created_at || "")
                      )
                      .map((fu) => (
                        <div
                          key={fu.id}
                          className="bg-white rounded-md border border-amber-100 p-3"
                          data-testid={`follow-up-entry-${fu.id}`}
                        >
                          <div className="flex items-start justify-between gap-3">
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 flex-wrap">
                                <Badge
                                  className={`${
                                    STATUS_COLORS[fu.status] ||
                                    "bg-slate-100 text-slate-700"
                                  } border font-normal`}
                                >
                                  {fu.status}
                                </Badge>
                                {fu.next_follow_up_date && (
                                  <span className="text-xs text-amber-800 inline-flex items-center gap-1">
                                    <CalendarClock className="w-3 h-3" />
                                    Next: {fu.next_follow_up_date}
                                    {fu.next_follow_up_time
                                      ? ` ${fu.next_follow_up_time}`
                                      : ""}
                                  </span>
                                )}
                              </div>
                              {fu.notes && (
                                <p className="mt-2 text-sm text-slate-700 whitespace-pre-wrap">
                                  {fu.notes}
                                </p>
                              )}
                              <div className="mt-2 text-xs text-slate-500">
                                Logged by {fu.created_by_name || "Unknown"} ·{" "}
                                {fu.created_at
                                  ? new Date(fu.created_at).toLocaleString("en-IN")
                                  : ""}
                              </div>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDelete(fu.id)}
                              className="text-rose-600 hover:text-rose-700 hover:bg-rose-50"
                              data-testid={`follow-up-delete-${fu.id}`}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default FollowUpTracker;
