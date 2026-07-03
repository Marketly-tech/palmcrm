/**
 * BulkDeleteBar — sticky toolbar that appears above a table whenever 1+ rows
 * are selected via the bulk-select checkboxes. Confirms via an AlertDialog
 * before invoking the caller-provided ``onConfirm`` async handler.
 *
 * Renders nothing when no rows are selected, so hosts can drop it in
 * unconditionally at the top of their table without layout jitter.
 */
import { useState } from "react";
import { Button } from "../ui/button";
import { Trash2, Loader2, X } from "lucide-react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../ui/alert-dialog";

const BulkDeleteBar = ({
  selectedCount,
  onConfirm,
  onClear,
  entityLabel = "item",
  entityLabelPlural = "items",
  previewNames = [],
  disabled = false,
  testId = "bulk-delete-bar",
}) => {
  const [open, setOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  if (selectedCount === 0 || disabled) return null;

  const label = selectedCount === 1 ? entityLabel : entityLabelPlural;

  const handleConfirm = async () => {
    setDeleting(true);
    try {
      await onConfirm();
      setOpen(false);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <>
      <div
        className="flex items-center justify-between gap-3 px-4 py-2 mb-3 rounded-lg border border-red-200 bg-red-50/70"
        data-testid={testId}
      >
        <div className="flex items-center gap-3 text-sm text-red-900">
          <span className="font-semibold" data-testid={`${testId}-count`}>
            {selectedCount} {label} selected
          </span>
          <button
            type="button"
            onClick={onClear}
            className="text-xs text-red-700 hover:text-red-900 underline"
            data-testid={`${testId}-clear`}
          >
            Clear
          </button>
        </div>
        <Button
          variant="destructive"
          size="sm"
          onClick={() => setOpen(true)}
          data-testid={`${testId}-trigger`}
        >
          <Trash2 className="w-4 h-4 mr-1.5" />
          Delete Selected ({selectedCount})
        </Button>
      </div>

      <AlertDialog open={open} onOpenChange={(v) => !deleting && setOpen(v)}>
        <AlertDialogContent data-testid={`${testId}-dialog`}>
          <AlertDialogHeader>
            <AlertDialogTitle>
              Delete {selectedCount} {label}?
            </AlertDialogTitle>
            <AlertDialogDescription asChild>
              <div className="space-y-2">
                <p>
                  This will permanently delete the selected {label}. This action
                  cannot be undone.
                </p>
                {previewNames.length > 0 && (
                  <ul
                    className="max-h-48 overflow-y-auto text-sm text-slate-700 bg-slate-50 border rounded p-2 list-disc pl-5"
                    data-testid={`${testId}-preview`}
                  >
                    {previewNames.slice(0, 20).map((n, i) => (
                      <li key={i} className="truncate">
                        {n}
                      </li>
                    ))}
                    {previewNames.length > 20 && (
                      <li className="italic text-slate-500">
                        …and {previewNames.length - 20} more
                      </li>
                    )}
                  </ul>
                )}
              </div>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel
              disabled={deleting}
              data-testid={`${testId}-cancel`}
            >
              <X className="w-4 h-4 mr-1" /> Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirm}
              disabled={deleting}
              className="bg-red-600 hover:bg-red-700"
              data-testid={`${testId}-confirm`}
            >
              {deleting ? (
                <Loader2 className="w-4 h-4 mr-1 animate-spin" />
              ) : (
                <Trash2 className="w-4 h-4 mr-1" />
              )}
              Delete {selectedCount} {label}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
};

export default BulkDeleteBar;
