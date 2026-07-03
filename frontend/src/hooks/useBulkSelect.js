/**
 * useBulkSelect — reusable multi-row selection state for tables.
 *
 * Tracks a Set of selected IDs and exposes helpers to toggle a single row,
 * toggle-all across the currently-visible rows, and clear the selection.
 * The consumer table wires the returned handlers into per-row checkboxes and
 * a header checkbox.
 */
import { useCallback, useMemo, useState } from "react";

export default function useBulkSelect(visibleIds = []) {
  const [selected, setSelected] = useState(() => new Set());

  const selectedIds = useMemo(() => Array.from(selected), [selected]);

  const toggle = useCallback((id) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  const isSelected = useCallback((id) => selected.has(id), [selected]);

  const isAllSelected = useMemo(
    () => visibleIds.length > 0 && visibleIds.every((id) => selected.has(id)),
    [visibleIds, selected]
  );

  const isPartiallySelected = useMemo(
    () =>
      !isAllSelected &&
      visibleIds.some((id) => selected.has(id)),
    [visibleIds, selected, isAllSelected]
  );

  const toggleAll = useCallback(() => {
    setSelected((prev) => {
      const next = new Set(prev);
      const allChecked = visibleIds.every((id) => next.has(id));
      if (allChecked) {
        visibleIds.forEach((id) => next.delete(id));
      } else {
        visibleIds.forEach((id) => next.add(id));
      }
      return next;
    });
  }, [visibleIds]);

  const clear = useCallback(() => setSelected(new Set()), []);

  return {
    selectedIds,
    selectedCount: selectedIds.length,
    isSelected,
    toggle,
    toggleAll,
    isAllSelected,
    isPartiallySelected,
    clear,
  };
}
