import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { ScrollArea } from "../ui/scroll-area";
import { Badge } from "../ui/badge";
import { Activity } from "lucide-react";

const RecentActivity = ({ activities }) => (
  <Card>
    <CardHeader>
      <CardTitle className="font-heading flex items-center gap-2">
        <Activity className="h-5 w-5 text-primary" />
        Recent Activity
      </CardTitle>
    </CardHeader>
    <CardContent>
      <ScrollArea className="h-64">
        {activities.length > 0 ? (
          <div className="space-y-3">
            {activities.map((activity) => (
              <div key={activity.id || activity.created_at} className="flex items-start gap-3 p-3 hover:bg-slate-50 rounded-lg">
                <div className="h-8 w-8 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0">
                  <Activity className="h-4 w-4 text-slate-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-slate-900">
                    <span className="font-medium">{activity.user_name}</span>{" "}
                    {activity.action} {activity.entity_type}
                  </p>
                  <p className="text-xs text-slate-500 truncate">{activity.details}</p>
                  <p className="text-xs text-slate-400 mt-1">{new Date(activity.timestamp).toLocaleString()}</p>
                </div>
                <Badge variant="outline" className="text-xs">{activity.entity_type}</Badge>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-center text-muted-foreground py-8">No recent activity</p>
        )}
      </ScrollArea>
    </CardContent>
  </Card>
);

export default RecentActivity;
