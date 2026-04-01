/**
 * ChecklistTab - Document checklist tracking component
 */
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Checkbox } from "../ui/checkbox";
import { Label } from "../ui/label";
import { CheckCircle } from "lucide-react";

const ChecklistTab = ({ checklist, onUpdateChecklist }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Document Checklist</CardTitle>
        <CardDescription>Track received documents</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {Object.entries(checklist.items || {}).map(([key, value]) => (
            <div key={key} className="flex items-center gap-3 p-3 border rounded-lg">
              <Checkbox
                id={key}
                checked={value}
                onCheckedChange={(checked) => onUpdateChecklist(key, checked)}
              />
              <Label htmlFor={key} className="flex-1 capitalize cursor-pointer">
                {key.replace(/_/g, " ")}
              </Label>
              {value && <CheckCircle className="w-5 h-5 text-green-500" />}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default ChecklistTab;
