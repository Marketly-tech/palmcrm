import { Card, CardContent } from "../ui/card";
import { Users, FileText, Clock } from "lucide-react";

const StatsCards = ({ stats }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Total Customers</p>
            <p className="text-3xl font-bold text-slate-900 mt-1">{stats?.total_customers || 0}</p>
          </div>
          <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
            <Users className="h-6 w-6 text-blue-600" />
          </div>
        </div>
      </CardContent>
    </Card>
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Pending Agreements</p>
            <p className="text-3xl font-bold text-slate-900 mt-1">{stats?.pending_agreements || 0}</p>
          </div>
          <div className="h-12 w-12 rounded-full bg-purple-100 flex items-center justify-center">
            <FileText className="h-6 w-6 text-purple-600" />
          </div>
        </div>
      </CardContent>
    </Card>
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Due This Week</p>
            <p className="text-3xl font-bold text-slate-900 mt-1">{stats?.payments_due_this_week || 0}</p>
          </div>
          <div className="h-12 w-12 rounded-full bg-amber-100 flex items-center justify-center">
            <Clock className="h-6 w-6 text-amber-600" />
          </div>
        </div>
      </CardContent>
    </Card>
  </div>
);

export default StatsCards;
