/**
 * Customer components index file.
 * Export all customer-related components for easy imports.
 */

// Tab components
export { default as ChecklistTab } from './ChecklistTab';
export { default as PaymentScheduleTab } from './PaymentScheduleTab';
export { default as DocumentsTab } from './DocumentsTab';
export { default as NotesTab } from './NotesTab';
export { default as UploadsTab } from './UploadsTab';
export { default as CommunicationTab } from './CommunicationTab';
export { default as DetailsTab } from './DetailsTab';
export { default as PaymentTrackingTab } from './PaymentTrackingTab';

// Card components
// (PaymentTrackingCard / TransactionsCard removed - logic now lives in PaymentTrackingTab subcomponents)

// Dialog components
export { default as EmailComposerDialog } from './EmailComposerDialog';

// Layout components
export { default as CustomerHeader } from './CustomerHeader';
export { default as CustomerQuickInfo } from './CustomerQuickInfo';

// Utility functions
export * from './utils';
