/**
 * PaymentScheduleTab - Payment schedule management component for customer profile
 * Displays milestone-based payment schedule with cumulative percentages
 */
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Plus, CreditCard } from "lucide-react";
import { formatCurrency } from "./utils";

const PaymentScheduleTab = ({
  paymentSchedule,
  onGenerateSchedule,
  onAddPayment,
}) => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newPayment, setNewPayment] = useState({
    installment_name: "",
    milestone: "",
    amount: "",
    due_date: "",
    percentage: "",
  });

  const handleAddPayment = async () => {
    if (!newPayment.installment_name || !newPayment.amount || !newPayment.due_date) {
      return;
    }
    
    await onAddPayment(newPayment);
    setNewPayment({
      installment_name: "",
      milestone: "",
      amount: "",
      due_date: "",
      percentage: "",
    });
    setDialogOpen(false);
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Payment Schedule</CardTitle>
          <CardDescription>Track all payment milestones</CardDescription>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={onGenerateSchedule} data-testid="generate-schedule-btn">
            Auto-Generate
          </Button>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button data-testid="add-payment-btn">
                <Plus className="w-4 h-4 mr-2" />
                Add Payment
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Payment Milestone</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label>Installment Name *</Label>
                  <Input
                    value={newPayment.installment_name}
                    onChange={(e) => setNewPayment({ ...newPayment, installment_name: e.target.value })}
                    placeholder="e.g., Booking Amount"
                  />
                </div>
                <div>
                  <Label>Milestone</Label>
                  <Select
                    value={newPayment.milestone}
                    onValueChange={(value) => setNewPayment({ ...newPayment, milestone: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select milestone" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="booking">Booking</SelectItem>
                      <SelectItem value="agreement">Agreement</SelectItem>
                      <SelectItem value="foundation">Foundation</SelectItem>
                      <SelectItem value="slab">Slab Completion</SelectItem>
                      <SelectItem value="handover">Handover</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Amount (₹) *</Label>
                  <Input
                    type="number"
                    value={newPayment.amount}
                    onChange={(e) => setNewPayment({ ...newPayment, amount: e.target.value })}
                  />
                </div>
                <div>
                  <Label>Due Date *</Label>
                  <Input
                    type="date"
                    value={newPayment.due_date}
                    onChange={(e) => setNewPayment({ ...newPayment, due_date: e.target.value })}
                  />
                </div>
                <Button onClick={handleAddPayment} className="w-full">
                  Add Payment
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        {paymentSchedule.items.length > 0 ? (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">#</TableHead>
                <TableHead>Particulars</TableHead>
                <TableHead className="text-center">%</TableHead>
                <TableHead className="text-center">Cumulative %</TableHead>
                <TableHead className="text-right">Amount</TableHead>
                <TableHead className="text-right">Cumulative Amt</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paymentSchedule.items.map((item, index) => {
                // Calculate cumulative percentage
                const cumulativePct = paymentSchedule.items
                  .slice(0, index + 1)
                  .reduce((sum, i) => sum + (i.percentage || 0), 0);
                return (
                  <TableRow key={item.id}>
                    <TableCell className="font-mono text-slate-500">{index + 1}</TableCell>
                    <TableCell className="font-medium max-w-xs">
                      <div className="truncate" title={item.installment_name}>
                        {item.installment_name}
                      </div>
                      {item.description && (
                        <div className="text-xs text-slate-500">{item.description}</div>
                      )}
                    </TableCell>
                    <TableCell className="text-center font-semibold">{item.percentage}%</TableCell>
                    <TableCell className="text-center font-semibold text-primary">{cumulativePct}%</TableCell>
                    <TableCell className="text-right font-mono">{formatCurrency(item.amount)}</TableCell>
                    <TableCell className="text-right font-mono text-primary font-semibold">{formatCurrency(item.cumulative)}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        ) : (
          <div className="text-center py-8 text-slate-500">
            <CreditCard className="w-12 h-12 mx-auto mb-4 text-slate-300" />
            <p>No payment schedule yet</p>
            <p className="text-sm mt-1">Click "Auto-Generate" to create from template</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PaymentScheduleTab;
