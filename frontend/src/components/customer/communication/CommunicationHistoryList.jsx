import { Badge } from "../../ui/badge";
import { Mail, Phone, MessageSquare } from "lucide-react";

const statusClass = (status) => {
  if (status === "sent") return "bg-green-50 text-green-700 border-green-300";
  if (status === "failed" || status === "error") return "bg-red-50 text-red-700 border-red-300";
  if (status?.includes("simulated") || status?.includes("mocked")) {
    return "bg-yellow-50 text-yellow-700 border-yellow-300";
  }
  return "bg-slate-50 text-slate-700 border-slate-300";
};

const CommunicationHistoryList = ({ communications }) => {
  if (communications.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500">
        <MessageSquare className="w-12 h-12 mx-auto mb-4 text-slate-300" />
        <p>No communication history yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {communications.map((comm) => (
        <div key={comm.id} className="p-4 border rounded-lg hover:border-slate-300 transition-colors">
          <div className="flex items-center gap-2 mb-2">
            {comm.channel === "email" ? (
              <Mail className="w-4 h-4 text-blue-500" />
            ) : (
              <Phone className="w-4 h-4 text-green-500" />
            )}
            <span className="font-medium capitalize">{comm.channel}</span>
            <span className="text-sm text-slate-500">- {comm.message_type}</span>
            <Badge variant="outline" className={`ml-auto ${statusClass(comm.status)}`}>
              {comm.status}
            </Badge>
          </div>
          <p className="text-sm text-slate-600 whitespace-pre-wrap line-clamp-3">{comm.content}</p>
          <p className="text-xs text-slate-400 mt-2">
            {new Date(comm.sent_at).toLocaleString()}
          </p>
        </div>
      ))}
    </div>
  );
};

export default CommunicationHistoryList;
