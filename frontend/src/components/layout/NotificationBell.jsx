/**
 * NotificationBell — header bell button surfacing every follow-up whose
 * status is not yet "Completed". Opens a popover listing items grouped by
 * urgency (past-due, today, upcoming, unscheduled). Each row deep-links to
 * the customer's Notes tab and has a one-click "Mark Completed" button so the
 * user can clear it after the call.
 */
import { useState, useEffect, useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import {
  Popover, PopoverContent, PopoverTrigger,
} from "../ui/popover";
import { Separator } from "../ui/separator";
import { Bell, CheckCircle2, PhoneCall, Loader2, CalendarClock } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const POLL_MS = 60_000;

const STATUS_COLORS = {
  Dialed: "bg-blue-100 text-blue-700",
  Connected: "bg-emerald-100 text-emerald-700",
  Unanswered: "bg-rose-100 text-rose-700",
  "Follow-up": "bg-amber-100 text-amber-700",
  Completed: "bg-violet-100 text-violet-700",
};

const bucketLabel = (item) => {
  if (item.is_past_due) return "Past Due";
  if (item.is_today) return "Today";
  if (item.next_follow_up_date) return "Upcoming";
  return "Unscheduled";
};

const bucketBadge = (label) => {
  switch (label) {
    case "Past Due":
      return "bg-rose-100 text-rose-700 border-rose-200";
    case "Today":
      return "bg-amber-100 text-amber-800 border-amber-200";
    case "Upcoming":
      return "bg-sky-100 text-sky-700 border-sky-200";
    default:
      return "bg-slate-100 text-slate-600 border-slate-200";
  }
};

const NotificationBell = () => {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [completingId, setCompletingId] = useState(null);
  const pollRef = useRef(null);

  const fetchPending = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/follow-ups/pending`);
      setItems(res.data || []);
    } catch {
      // silent — endpoint may 401 on logout
    }
  }, []);

  // Initial fetch + lightweight polling so the count badge stays fresh.
  useEffect(() => {
    setLoading(true);
    fetchPending().finally(() => setLoading(false));
    pollRef.current = setInterval(fetchPending, POLL_MS);
    return () => clearInterval(pollRef.current);
  }, [fetchPending]);

  const handleMarkCompleted = async (item, e) => {
    e.stopPropagation();
    setCompletingId(item.follow_up_id);
    try {
      await axios.patch(
        `${API}/customers/${item.customer_id}/follow-ups/${item.follow_up_id}`,
        { status: "Completed" }
      );
      toast.success(`Marked completed for ${item.customer_name}`);
      // Optimistic removal
      setItems((prev) => prev.filter((x) => x.follow_up_id !== item.follow_up_id));
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Failed to mark completed");
    } finally {
      setCompletingId(null);
    }
  };

  const handleOpenCallLog = (item) => {
    setOpen(false);
    // Deep-link to the customer's Notes tab where the Calling & Follow-up
    // Tracker lives. CustomerDetailPage reads ?tab= from the URL.
    navigate(`/customers/${item.customer_id}?tab=notes&focus=${item.follow_up_id}`);
  };

  const pastDueCount = items.filter((i) => i.is_past_due).length;
  const todayCount = items.filter((i) => i.is_today).length;
  const totalCount = items.length;
  const headlineCount = pastDueCount + todayCount;

  // Group items by bucket for the popover
  const grouped = items.reduce((acc, item) => {
    const label = bucketLabel(item);
    if (!acc[label]) acc[label] = [];
    acc[label].push(item);
    return acc;
  }, {});
  const bucketOrder = ["Past Due", "Today", "Upcoming", "Unscheduled"];

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="relative h-9 w-9"
          data-testid="notification-bell-btn"
          aria-label={`Follow-up notifications (${totalCount} pending)`}
        >
          <Bell className="w-5 h-5 text-slate-600" />
          {totalCount > 0 && (
            <span
              className={`absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 rounded-full text-[10px] font-semibold flex items-center justify-center ring-2 ring-white ${
                headlineCount > 0
                  ? "bg-rose-600 text-white"
                  : "bg-slate-400 text-white"
              }`}
              data-testid="notification-bell-count"
            >
              {totalCount > 99 ? "99+" : totalCount}
            </span>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent
        align="end"
        className="w-[420px] p-0 max-h-[80vh] overflow-hidden flex flex-col"
        data-testid="notification-bell-popover"
      >
        <div className="px-4 py-3 border-b bg-gradient-to-br from-amber-50 to-orange-50 flex items-start justify-between gap-3">
          <div>
            <div className="font-semibold text-slate-900 flex items-center gap-2">
              <PhoneCall className="w-4 h-4 text-amber-700" />
              Follow-ups
            </div>
            <div className="text-xs text-slate-600 mt-0.5">
              {totalCount === 0
                ? "You're all caught up — no pending follow-ups."
                : `${totalCount} pending · ${pastDueCount} past-due · ${todayCount} today`}
            </div>
          </div>
          {loading && (
            <Loader2 className="w-4 h-4 animate-spin text-amber-700 mt-1" />
          )}
        </div>

        <div className="overflow-y-auto flex-1 min-h-[120px]">
          {totalCount === 0 ? (
            <div className="px-4 py-10 text-center text-sm text-slate-500">
              <CheckCircle2 className="w-10 h-10 mx-auto mb-2 text-emerald-300" />
              No pending calls. New follow-ups will appear here.
            </div>
          ) : (
            bucketOrder
              .filter((b) => grouped[b]?.length)
              .map((label) => (
                <div key={label} className="border-b last:border-b-0">
                  <div className="px-4 py-2 sticky top-0 bg-white/95 backdrop-blur z-10 flex items-center justify-between">
                    <Badge
                      variant="outline"
                      className={`${bucketBadge(label)} text-xs`}
                    >
                      {label}
                    </Badge>
                    <span className="text-xs text-slate-500">
                      {grouped[label].length} item
                      {grouped[label].length === 1 ? "" : "s"}
                    </span>
                  </div>
                  <Separator />
                  <div>
                    {grouped[label].map((item) => (
                      <div
                        role="button"
                        tabIndex={0}
                        key={item.follow_up_id}
                        onClick={() => handleOpenCallLog(item)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" || e.key === " ") {
                            e.preventDefault();
                            handleOpenCallLog(item);
                          }
                        }}
                        className="w-full text-left px-4 py-3 hover:bg-amber-50/60 transition-colors border-b last:border-b-0 focus:outline-none focus:bg-amber-50 cursor-pointer"
                        data-testid={`notification-item-${item.follow_up_id}`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium text-slate-900 truncate">
                              {item.customer_name}
                              {item.unit_number && (
                                <span className="ml-1 text-xs font-normal text-slate-500">
                                  · {item.tower}-{item.unit_number}
                                </span>
                              )}
                            </div>
                            <div className="mt-1 flex flex-wrap items-center gap-1.5">
                              <Badge
                                className={`${
                                  STATUS_COLORS[item.status] ||
                                  "bg-slate-100 text-slate-700"
                                } border-0 text-[10px] font-normal`}
                              >
                                {item.status}
                              </Badge>
                              <span className="text-xs text-slate-500 truncate">
                                {item.stage_name}
                              </span>
                            </div>
                            {item.next_follow_up_date && (
                              <div className="mt-1 text-xs text-slate-600 inline-flex items-center gap-1">
                                <CalendarClock className="w-3 h-3" />
                                {item.next_follow_up_date}
                                {item.next_follow_up_time
                                  ? ` ${item.next_follow_up_time}`
                                  : ""}
                              </div>
                            )}
                            {item.notes && (
                              <div className="mt-1 text-xs text-slate-500 line-clamp-2">
                                {item.notes}
                              </div>
                            )}
                          </div>
                          <Button
                            variant="outline"
                            size="sm"
                            className="h-7 px-2 text-xs border-emerald-200 text-emerald-700 hover:bg-emerald-50 hover:text-emerald-800 shrink-0"
                            onClick={(e) => handleMarkCompleted(item, e)}
                            disabled={completingId === item.follow_up_id}
                            data-testid={`notification-complete-${item.follow_up_id}`}
                            aria-label="Mark this follow-up completed"
                          >
                            {completingId === item.follow_up_id ? (
                              <Loader2 className="w-3 h-3 animate-spin" />
                            ) : (
                              <>
                                <CheckCircle2 className="w-3 h-3 mr-1" />
                                Done
                              </>
                            )}
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
};

export default NotificationBell;
