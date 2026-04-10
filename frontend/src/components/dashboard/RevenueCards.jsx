import { Card, CardContent } from "../ui/card";
import { IndianRupee, Clock } from "lucide-react";

const RevenueCards = ({ stats, formatCurrency }) => (
  <>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <Card className="hover:shadow-md transition-shadow border-green-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Revenue Collected</p>
              <p className="text-3xl font-bold text-green-600 mt-1">{formatCurrency(stats?.total_revenue || 0)}</p>
              <p className="text-sm text-green-600 mt-1">{(100 - (stats?.pending_percentage || 0)).toFixed(1)}% collected</p>
            </div>
            <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
              <IndianRupee className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </CardContent>
      </Card>
      <Card className="hover:shadow-md transition-shadow border-amber-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Pending Payments</p>
              <p className="text-3xl font-bold text-amber-600 mt-1">{formatCurrency(stats?.total_pending || 0)}</p>
              <p className="text-sm text-amber-600 mt-1">{(stats?.pending_percentage || 0).toFixed(1)}% pending</p>
            </div>
            <div className="h-12 w-12 rounded-full bg-amber-100 flex items-center justify-center">
              <Clock className="h-6 w-6 text-amber-600" />
            </div>
          </div>
          <div className="mt-4">
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div className="h-full bg-green-500 transition-all duration-500" style={{ width: `${100 - (stats?.pending_percentage || 0)}%` }} />
            </div>
            <p className="text-xs text-muted-foreground mt-1">Payment Collection Progress</p>
          </div>
        </CardContent>
      </Card>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <Card className="hover:shadow-md transition-shadow border-blue-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Flat Value</p>
              <p className="text-3xl font-bold text-blue-600 mt-1">{formatCurrency(stats?.total_flat_value || 0)}</p>
              <p className="text-sm text-slate-500 mt-1">Combined value of all units</p>
            </div>
            <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
              <IndianRupee className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </CardContent>
      </Card>
      <Card className="hover:shadow-md transition-shadow border-orange-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Balance</p>
              <p className="text-3xl font-bold text-orange-600 mt-1">{formatCurrency(stats?.total_balance || 0)}</p>
              <p className="text-sm text-slate-500 mt-1">Outstanding amount to collect</p>
            </div>
            <div className="h-12 w-12 rounded-full bg-orange-100 flex items-center justify-center">
              <IndianRupee className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </>
);

export default RevenueCards;
