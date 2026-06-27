/**
 * Web-Audio based 2-tone "follow-up" chime — synthesised on the fly so we don't
 * have to ship any audio assets. Safe to call from any user-triggered event;
 * silently no-ops if the browser hasn't unlocked audio yet.
 */
let cachedCtx = null;

const getCtx = () => {
  if (cachedCtx) return cachedCtx;
  if (typeof window === "undefined") return null;
  const Ctor = window.AudioContext || window.webkitAudioContext;
  if (!Ctor) return null;
  cachedCtx = new Ctor();
  return cachedCtx;
};

const playTone = (ctx, freq, startAt, duration = 0.18) => {
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = "sine";
  osc.frequency.value = freq;
  // Gentle attack/release so it doesn't sound like a beep buzzer.
  gain.gain.setValueAtTime(0.0001, startAt);
  gain.gain.exponentialRampToValueAtTime(0.25, startAt + 0.02);
  gain.gain.exponentialRampToValueAtTime(0.0001, startAt + duration);
  osc.connect(gain).connect(ctx.destination);
  osc.start(startAt);
  osc.stop(startAt + duration + 0.02);
};

export const playFollowUpChime = () => {
  try {
    const ctx = getCtx();
    if (!ctx) return;
    if (ctx.state === "suspended") {
      ctx.resume().catch(() => {});
    }
    const now = ctx.currentTime;
    // Pleasant ascending 2-tone (C5 → E5)
    playTone(ctx, 523.25, now, 0.18);
    playTone(ctx, 659.25, now + 0.2, 0.22);
  } catch {
    /* no-op — audio is best-effort */
  }
};
