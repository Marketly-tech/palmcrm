import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Badge } from "../ui/badge";
import { Label } from "../ui/label";

const GeneralSettingsTab = ({ user, getRoleBadge }) => (
  <Card>
    <CardHeader>
      <CardTitle>General Settings</CardTitle>
      <CardDescription>System configuration and preferences</CardDescription>
    </CardHeader>
    <CardContent className="space-y-6">
      <div className="space-y-4">
        <h3 className="font-semibold text-lg">Your Profile</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label className="text-slate-500">Name</Label>
            <p className="font-medium">{user?.name}</p>
          </div>
          <div>
            <Label className="text-slate-500">Email</Label>
            <p className="font-medium">{user?.email}</p>
          </div>
          <div>
            <Label className="text-slate-500">Role</Label>
            <Badge className={getRoleBadge(user?.role)}>{user?.role}</Badge>
          </div>
          <div>
            <Label className="text-slate-500">Phone</Label>
            <p className="font-medium">{user?.phone || "-"}</p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="font-semibold text-lg">Integration Status</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 border rounded-lg">
            <div className="flex items-center justify-between">
              <span>Google Forms Webhook</span>
              <Badge variant="outline">Ready</Badge>
            </div>
            <p className="text-sm text-slate-500 mt-1">Endpoint: /api/webhook/google-form</p>
          </div>
          <div className="p-4 border rounded-lg">
            <div className="flex items-center justify-between">
              <span>Email (SendGrid)</span>
              <Badge className="bg-green-100 text-green-700">Active</Badge>
            </div>
            <p className="text-sm text-slate-500 mt-1">Email service configured and ready</p>
          </div>
          <div className="p-4 border rounded-lg">
            <div className="flex items-center justify-between">
              <span>WhatsApp (Twilio)</span>
              <Badge className="bg-amber-100 text-amber-700">Pending</Badge>
            </div>
            <p className="text-sm text-slate-500 mt-1">Configure Twilio credentials for production</p>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
);

export default GeneralSettingsTab;
