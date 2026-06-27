/**
 * useFollowUpReminders — polls the backend every minute for follow-ups whose
 * ``next_follow_up_date`` (and optional ``next_follow_up_time``) has arrived,
 * and plays a chime + browser notification once per entry per session.
 *
 * Mount this at the authenticated layout level (e.g. Dashboard layout) so it
 * runs anywhere inside the app, not just on the customer detail page.
 */
import { useEffect, useRef } from "react";
import axios from "axios";
import { toast } from "sonner";
import { playFollowUpChime } from "../utils/followUpSound";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const POLL_MS = 60_000;

const isDue = (fu) => {
  if (!fu.next_follow_up_date) return false;
  const now = new Date();
  const dateStr = fu.next_follow_up_date;
  // Treat any past-due entry as due (so we never miss it after a refresh).
  if (dateStr < now.toISOString().slice(0, 10)) return true;
  if (dateStr > now.toISOString().slice(0, 10)) return false;
  // Same day — compare against time if provided, else fire any time today.
  if (!fu.next_follow_up_time) return true;
  const [h, m] = fu.next_follow_up_time.split(":").map((n) => parseInt(n, 10));
  const target = new Date();
  target.setHours(h || 0, m || 0, 0, 0);
  return now >= target;
};

export const useFollowUpReminders = (enabled = true) => {
  const firedRef = useRef(new Set());

  useEffect(() => {
    if (!enabled) return undefined;
    // Politely ask for permission once (no-op if already granted/denied).
    if (typeof Notification !== "undefined" && Notification.permission === "default") {
      Notification.requestPermission().catch(() => {});
    }

    let cancelled = false;
    const tick = async () => {
      try {
        const res = await axios.get(`${API}/follow-ups/upcoming`);
        if (cancelled) return;
        (res.data || []).forEach((fu) => {
          if (!isDue(fu)) return;
          if (firedRef.current.has(fu.follow_up_id)) return;
          firedRef.current.add(fu.follow_up_id);

          playFollowUpChime();
          const title = `Follow-up due: ${fu.customer_name || "Customer"}`;
          const body = `${fu.stage_name || ""} • ${fu.status || ""}${
            fu.notes ? ` — ${fu.notes.slice(0, 80)}` : ""
          }`;
          if (
            typeof Notification !== "undefined" &&
            Notification.permission === "granted"
          ) {
            try {
              new Notification(title, { body });
            } catch {
              /* some browsers throw on bg tabs */
            }
          }
          toast.message(title, { description: body, duration: 8000 });
        });
      } catch {
        // silent — endpoint may 401 on logout, etc.
      }
    };

    // Fire once immediately, then every minute.
    tick();
    const interval = setInterval(tick, POLL_MS);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [enabled]);
};

export default useFollowUpReminders;
