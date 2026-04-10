import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Button } from "../ui/button";
import { FileText, IndianRupee, Activity } from "lucide-react";

const ExportDataCard = ({ onExport }) => (
  <Card>
    <CardHeader>
      <CardTitle className="font-heading flex items-center gap-2">
        <FileText className="h-5 w-5 text-primary" />
        Export CRM Data
      </CardTitle>
      <CardDescription>Download all data for reporting and analysis</CardDescription>
    </CardHeader>
    <CardContent className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <Button variant="outline" className="h-20 flex flex-col items-center justify-center gap-2" onClick={() => onExport("customers", "csv")} data-testid="export-customers-csv">
          <FileText className="h-6 w-6 text-green-600" /><span className="text-sm">Customers CSV</span>
        </Button>
        <Button variant="outline" className="h-20 flex flex-col items-center justify-center gap-2" onClick={() => onExport("customers", "excel")} data-testid="export-customers-excel">
          <FileText className="h-6 w-6 text-blue-600" /><span className="text-sm">Customers Excel</span>
        </Button>
        <Button variant="outline" className="h-20 flex flex-col items-center justify-center gap-2" onClick={() => onExport("payments", "csv")} data-testid="export-payments-csv">
          <IndianRupee className="h-6 w-6 text-amber-600" /><span className="text-sm">Payments CSV</span>
        </Button>
        <Button variant="outline" className="h-20 flex flex-col items-center justify-center gap-2 opacity-50" disabled>
          <Activity className="h-6 w-6 text-purple-600" /><span className="text-sm">Activity Logs</span>
        </Button>
      </div>
      <p className="text-xs text-muted-foreground text-center">Click to download data in your preferred format</p>
    </CardContent>
  </Card>
);

export default ExportDataCard;
