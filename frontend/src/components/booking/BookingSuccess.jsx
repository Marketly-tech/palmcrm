import { Card, CardContent } from "../ui/card";
import { CheckCircle, Mail } from "lucide-react";

const BookingSuccess = ({ submissionResult, email }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 to-pink-100 flex items-center justify-center p-4">
      <Card className="max-w-lg w-full">
        <CardContent className="p-8 text-center">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Booking Submitted!</h2>
          <p className="text-slate-600 mb-6">
            Thank you for your booking. Our team will contact you shortly.
          </p>
          <div className="bg-slate-50 p-4 rounded-lg text-left mb-6">
            <p className="text-sm text-slate-500">Reference Number</p>
            <p className="text-lg font-mono font-bold text-primary">{submissionResult?.customer_id}</p>
          </div>
          <div className="bg-green-50 border border-green-200 p-4 rounded-lg mb-4">
            <div className="flex items-center justify-center gap-2 text-green-700">
              <Mail className="w-5 h-5" />
              <span className="font-medium">Welcome Email Sent!</span>
            </div>
            <p className="text-sm text-green-600 mt-2">
              A confirmation email with your <strong>Price Breakup</strong> and <strong>Terms & Conditions</strong> has been sent to:
            </p>
            <p className="text-sm font-medium text-green-800 mt-1">{email}</p>
          </div>
          <p className="text-xs text-slate-400">
            Please check your inbox (and spam folder) for the booking confirmation.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default BookingSuccess;
