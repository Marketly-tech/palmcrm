/**
 * Tiny logger that no-ops in production builds.
 * Use in catch blocks instead of console.error to avoid leaking
 * debug info or impacting performance in production.
 *
 * Usage:
 *   import { logError } from "../utils/logger";
 *   try { ... } catch (e) { logError("Failed to fetch foo", e); }
 */
const isProd = process.env.NODE_ENV === "production";

export const logError = (...args) => {
  if (!isProd) {
    // eslint-disable-next-line no-console
    console.error(...args);
  }
};

export const logWarn = (...args) => {
  if (!isProd) {
    // eslint-disable-next-line no-console
    console.warn(...args);
  }
};
