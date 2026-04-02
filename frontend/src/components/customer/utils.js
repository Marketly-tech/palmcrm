/**
 * Customer utility functions for formatting and calculations.
 */

/**
 * Format currency in Indian format
 */
export const formatCurrency = (value) => {
  if (value === null || value === undefined) return '₹0';
  const num = parseFloat(value);
  if (isNaN(num)) return '₹0';
  return `₹${num.toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
};

/**
 * Get status badge color class based on status
 */
export const getStatusBadge = (status) => {
  const statusColors = {
    qualified: 'bg-emerald-100 text-emerald-700 border-emerald-300',
    agreement_pending: 'bg-amber-100 text-amber-700 border-amber-300',
    agreement_done: 'bg-blue-100 text-blue-700 border-blue-300',
    pending_approval: 'bg-yellow-100 text-yellow-700 border-yellow-300',
    registration_done: 'bg-purple-100 text-purple-700 border-purple-300',
    disbursement: 'bg-purple-100 text-purple-700 border-purple-300',
    pending: 'bg-red-100 text-red-700 border-red-300',
    paid: 'bg-green-100 text-green-700 border-green-300',
    partial: 'bg-yellow-100 text-yellow-700 border-yellow-300',
    overdue: 'bg-red-100 text-red-700 border-red-300',
  };
  return statusColors[status] || 'bg-slate-100 text-slate-700 border-slate-300';
};

/**
 * Get agreement status color class
 */
export const getAgreementStatusColor = (status) => {
  const colors = {
    signed: 'bg-green-100 text-green-700 border-green-300',
    registered: 'bg-blue-100 text-blue-700 border-blue-300',
    sent: 'bg-yellow-100 text-yellow-700 border-yellow-300',
    disbursement: 'bg-purple-100 text-purple-700 border-purple-300',
    draft: 'bg-slate-100 text-slate-700 border-slate-300',
  };
  return colors[status] || 'bg-slate-100 text-slate-700 border-slate-300';
};

/**
 * Format date for display
 */
export const formatDate = (dateString) => {
  if (!dateString) return '-';
  try {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return dateString;
  }
};

/**
 * Format phone number for display
 */
export const formatPhone = (phone) => {
  if (!phone) return '-';
  // Remove non-digits
  const digits = phone.replace(/\D/g, '');
  if (digits.length === 10) {
    return `${digits.slice(0, 5)} ${digits.slice(5)}`;
  }
  return phone;
};

/**
 * Calculate total received from transactions only.
 * booking_amount is already included as transaction entries, so we don't add it separately.
 */
export const calculateTotalReceived = (transactions) => {
  return transactions.reduce((sum, txn) => sum + (txn.amount || 0), 0);
};

/**
 * Calculate received percentage
 */
export const calculateReceivedPercentage = (totalReceived, totalPrice) => {
  if (!totalPrice || totalPrice <= 0) return 0;
  return ((totalReceived / totalPrice) * 100).toFixed(1);
};

/**
 * Get gender display text
 */
export const getGenderDisplay = (gender) => {
  const genderMap = {
    male: 'Male (S/o)',
    female: 'Female (D/o)',
    spouse: 'Spouse (W/o)',
  };
  return genderMap[gender] || gender || '-';
};

/**
 * Sanitize for JSON (remove _id fields)
 */
export const sanitizeForApi = (obj) => {
  if (!obj) return obj;
  const { _id, ...rest } = obj;
  return rest;
};
