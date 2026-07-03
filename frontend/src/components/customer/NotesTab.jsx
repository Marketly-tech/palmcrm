/**
 * NotesTab - Customer notes management component
 * Allows users to add, view, and delete notes for a customer.
 * Renders the multi-level FollowUpTracker above the notes section so the
 * sales/accounts team can log stage-tied follow-ups in the same view.
 */
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import { Separator } from "../ui/separator";
import { Checkbox } from "../ui/checkbox";
import { Plus, Loader2, Trash2, FileText } from "lucide-react";
import FollowUpTracker from "./FollowUpTracker";
import BulkDeleteBar from "../common/BulkDeleteBar";
import useBulkSelect from "../../hooks/useBulkSelect";

const NotesTab = ({
  notes,
  onAddNote,
  onDeleteNote,
  onBulkDeleteNotes,
  isAdmin = false,
  isAccountsRole = false,
  customerId,
}) => {
  const [newNote, setNewNote] = useState("");
  const [addingNote, setAddingNote] = useState(false);
  const bulk = useBulkSelect(notes.map((n) => n.id));
  const selectedNotes = notes.filter((n) => bulk.isSelected(n.id));

  const handleAddNote = async () => {
    if (!newNote.trim()) return;
    setAddingNote(true);
    try {
      await onAddNote(newNote);
      setNewNote("");
    } finally {
      setAddingNote(false);
    }
  };

  const handleBulk = async () => {
    await onBulkDeleteNotes?.(bulk.selectedIds);
    bulk.clear();
  };

  return (
    <div className="space-y-6">
      {customerId && <FollowUpTracker customerId={customerId} isAdmin={isAdmin} />}
      <Card>
      <CardHeader>
        <CardTitle>Customer Notes</CardTitle>
        <CardDescription>Keep track of important information and follow-ups</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {isAdmin && (
          <BulkDeleteBar
            selectedCount={bulk.selectedCount}
            onClear={bulk.clear}
            onConfirm={handleBulk}
            entityLabel="note"
            entityLabelPlural="notes"
            previewNames={selectedNotes.map((n) => (n.content || "").slice(0, 80))}
            testId="bulk-delete-notes"
          />
        )}
        {/* Add Note Input */}
        <div className="flex gap-2">
          <Textarea
            placeholder="Add a note about this customer..."
            value={newNote}
            onChange={(e) => setNewNote(e.target.value)}
            className="flex-1"
            rows={2}
            data-testid="new-note-input"
          />
          <Button 
            onClick={handleAddNote} 
            disabled={addingNote || !newNote.trim()}
            data-testid="add-note-btn"
          >
            {addingNote ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <>
                <Plus className="h-4 w-4 mr-1" />
                Add Note
              </>
            )}
          </Button>
        </div>
        
        <Separator />
        
        {/* Notes List */}
        {notes.length > 0 ? (
          <div className="space-y-3">
            {notes.map((note) => (
              <div key={note.id} className="p-4 bg-slate-50 rounded-lg border">
                <div className="flex items-start justify-between gap-3">
                  {isAdmin && (
                    <Checkbox
                      checked={bulk.isSelected(note.id)}
                      onCheckedChange={() => bulk.toggle(note.id)}
                      aria-label="Select note"
                      className="mt-1"
                      data-testid={`bulk-select-note-${note.id}`}
                    />
                  )}
                  <div className="flex-1">
                    <p className="text-slate-800 whitespace-pre-wrap">{note.content}</p>
                    <div className="flex items-center gap-2 mt-2 text-xs text-slate-500">
                      <span>By {note.created_by_name}</span>
                      <span>•</span>
                      <span>{new Date(note.created_at).toLocaleString('en-IN')}</span>
                    </div>
                  </div>
                  {!isAccountsRole && (
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      onClick={() => onDeleteNote(note.id)}
                      data-testid={`delete-note-${note.id}`}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-slate-500">
            <FileText className="w-12 h-12 mx-auto mb-4 text-slate-300" />
            <p>No notes yet</p>
            <p className="text-sm mt-1">Add notes to keep track of important information</p>
          </div>
        )}
      </CardContent>
    </Card>
    </div>
  );
};

export default NotesTab;
