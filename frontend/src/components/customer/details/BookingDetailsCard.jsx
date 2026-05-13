import { Card, CardContent, CardHeader, CardTitle } from "../../ui/card";
import { Label } from "../../ui/label";
import { Input } from "../../ui/input";
import { Button } from "../../ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../../ui/select";
import { Pencil } from "lucide-react";
import { CANONICAL_BANKS } from "../../../utils/banks";

const BookingDetailsCard = ({
  customer,
  user,
  editingBooking,
  setEditingBooking,
  savingBooking,
  bookingForm,
  setBookingForm,
  handleSaveBookingDetails,
  formatCurrency,
}) => {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Booking Details</CardTitle>
        {user?.role === "admin" && !editingBooking && (
          <Button variant="outline" size="sm" onClick={() => setEditingBooking(true)} data-testid="edit-booking-btn">
            <Pencil className="w-4 h-4 mr-1" /> Edit
          </Button>
        )}
      </CardHeader>
      <CardContent>
        {editingBooking ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit-finance-type">Finance Type</Label>
                <Select value={bookingForm.finance_type} onValueChange={(v) => setBookingForm(prev => ({ ...prev, finance_type: v }))}>
                  <SelectTrigger id="edit-finance-type" data-testid="edit-finance-type">
                    <SelectValue placeholder="Select" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="self">Self</SelectItem>
                    <SelectItem value="loan">Loan</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="edit-finance-bank">Bank</Label>
                <Select
                  value={CANONICAL_BANKS.includes(bookingForm.finance_bank) ? bookingForm.finance_bank : (bookingForm.finance_bank ? "__other__" : "")}
                  onValueChange={(v) => setBookingForm(prev => ({ ...prev, finance_bank: v === "__other__" ? "" : v }))}
                >
                  <SelectTrigger id="edit-finance-bank" data-testid="edit-finance-bank">
                    <SelectValue placeholder="Select bank" />
                  </SelectTrigger>
                  <SelectContent>
                    {CANONICAL_BANKS.map((b) => (
                      <SelectItem key={b} value={b}>{b}</SelectItem>
                    ))}
                    <SelectItem value="__other__">Other (type below)</SelectItem>
                  </SelectContent>
                </Select>
                {!CANONICAL_BANKS.includes(bookingForm.finance_bank) && (
                  <Input
                    className="mt-2"
                    placeholder="Enter bank name"
                    value={bookingForm.finance_bank}
                    onChange={(e) => setBookingForm(prev => ({ ...prev, finance_bank: e.target.value }))}
                    data-testid="edit-finance-bank-other"
                  />
                )}
              </div>
              <div>
                <Label htmlFor="edit-booking-amount">Booking Amount</Label>
                <Input id="edit-booking-amount" data-testid="edit-booking-amount" type="number" value={bookingForm.booking_amount} onChange={(e) => setBookingForm(prev => ({ ...prev, booking_amount: e.target.value }))} />
              </div>
              <div>
                <Label htmlFor="edit-booking-date">Booking Date</Label>
                <Input id="edit-booking-date" data-testid="edit-booking-date" type="date" value={bookingForm.booking_date} onChange={(e) => setBookingForm(prev => ({ ...prev, booking_date: e.target.value }))} />
              </div>
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" size="sm" onClick={() => setEditingBooking(false)} data-testid="cancel-booking-edit">Cancel</Button>
              <Button size="sm" onClick={handleSaveBookingDetails} disabled={savingBooking} data-testid="save-booking-btn">
                {savingBooking ? "Saving..." : "Save"}
              </Button>
            </div>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Finance Type</Label>
                <p className="text-slate-700 mt-1 capitalize">{customer.finance_type || "Self"}</p>
              </div>
              <div>
                <Label>Bank</Label>
                <p className="text-slate-700 mt-1">{customer.finance_bank || "-"}</p>
              </div>
              <div>
                <Label>Booking Amount</Label>
                <p className="text-slate-700 mt-1">{formatCurrency(customer.booking_amount)}</p>
              </div>
              <div>
                <Label>Booking Date</Label>
                <p className="text-slate-700 mt-1">{customer.booking_date || "-"}</p>
              </div>
            </div>
            {(customer.transaction_details || customer.transaction_date || customer.transaction_bank) && (
              <div className="mt-4 pt-4 border-t">
                <p className="font-medium text-slate-700 mb-3">Transaction Details</p>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Transaction Date</Label>
                    <p className="text-slate-700 mt-1">{customer.transaction_date || "-"}</p>
                  </div>
                  <div>
                    <Label>Transaction Bank</Label>
                    <p className="text-slate-700 mt-1">{customer.transaction_bank || "-"}</p>
                  </div>
                </div>
                {customer.transaction_details && (
                  <div className="mt-2">
                    <Label>Transaction Reference</Label>
                    <p className="text-slate-700 mt-1">{customer.transaction_details}</p>
                  </div>
                )}
              </div>
            )}
          </>
        )}
        {customer.remarks && (
          <div className="mt-4 pt-4 border-t">
            <Label>Remarks</Label>
            <p className="text-slate-700 mt-1">{customer.remarks}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default BookingDetailsCard;
