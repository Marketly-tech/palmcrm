/**
 * Canonical bank list (frontend mirror of backend utils/banks.py).
 *
 * Used by Booking Details edit form and public Payment step so all
 * future entries use exactly one spelling per bank — preventing the
 * "HDFC vs HDFC BANK" duplicates seen in the customer filter dropdown.
 */
export const CANONICAL_BANKS = [
  "HDFC Bank",
  "Bank of Baroda",
  "TATA Capital",
  "State Bank of India",
  "ICICI Bank",
  "Axis Bank",
  "Punjab National Bank",
  "Kotak Mahindra Bank",
  "Canara Bank",
  "Bajaj Housing Finance",
];
