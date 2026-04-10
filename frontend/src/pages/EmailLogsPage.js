import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { Mail, Search, ChevronLeft, ChevronRight, ExternalLink, Inbox, ChevronDown, ChevronUp, Eye } from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

const EmailLogsPage = () => {
  const navigate = useNavigate();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [expandedId, setExpandedId] = useState(null);

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page, limit: 30 });
      if (statusFilter !== "all") params.append("status", statusFilter);
      if (search) params.append("search", search);
      const res = await axios.get(`${API}/email-logs?${params}`);
      setLogs(res.data.logs || []);
      setTotalPages(res.data.total_pages || 1);
      setTotal(res.data.total || 0);
    } catch {
      setLogs([]);
    } finally {
      setLoading(false);
    }
  }, [page, statusFilter, search]);

  useEffect(() => { fetchLogs(); }, [fetchLogs]);

  const handleSearch = (e) => {
    e.preventDefault();
    setSearch(searchInput);
    setPage(1);
  };

  const getStatusBadge = (status) => {
    if (status === "sent") return "bg-green-50 text-green-700 border-green-300";
    if (status === "failed" || status === "error") return "bg-red-50 text-red-700 border-red-300";
    if (status?.includes("simulated") || status?.includes("mocked")) return "bg-yellow-50 text-yellow-700 border-yellow-300";
    return "bg-slate-50 text-slate-700 border-slate-300";
  };

  return (
    <div className="space-y-6" data-testid="email-logs-page">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Email Tracking</h1>
        <p className="text-sm text-slate-500 mt-1">Track all outbound emails sent from the CRM</p>
      </div>

      {/* Info Banner */}
      <div className="flex items-center gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <Inbox className="w-5 h-5 text-blue-600 flex-shrink-0" />
        <div>
          <p className="text-sm font-medium text-blue-800">Inbox & Replies</p>
          <p className="text-xs text-blue-600">
            Customer replies will appear in your email inbox (crm@rrlbuildersanddevelopers.com). 
            This page tracks all outbound emails sent from the CRM. Full inbox integration can be added via SendGrid Inbound Parse.
          </p>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Mail className="w-5 h-5 text-primary" />
                All Sent Emails
              </CardTitle>
              <CardDescription>{total} total emails tracked</CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <form onSubmit={handleSearch} className="flex gap-2">
                <Input
                  placeholder="Search by customer, subject..."
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  className="w-56"
                  data-testid="email-search-input"
                />
                <Button type="submit" variant="outline" size="sm">
                  <Search className="w-4 h-4" />
                </Button>
              </form>
              <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setPage(1); }}>
                <SelectTrigger className="w-36" data-testid="email-status-filter">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="sent">Sent</SelectItem>
                  <SelectItem value="failed">Failed</SelectItem>
                  <SelectItem value="simulated">Simulated</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-12 text-slate-500">Loading emails...</div>
          ) : logs.length > 0 ? (
            <div className="space-y-3">
              {logs.map((log) => (
                <div
                  key={log.id}
                  className="border rounded-lg hover:border-slate-300 transition-colors overflow-hidden"
                  data-testid={`email-log-${log.id}`}
                >
                  <div
                    className="p-4 cursor-pointer"
                    onClick={() => setExpandedId(expandedId === log.id ? null : log.id)}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <Mail className="w-4 h-4 text-blue-500 flex-shrink-0" />
                          <span className="font-medium text-sm truncate">{log.customer_name}</span>
                          <span className="text-xs text-slate-400">({log.customer_display_id})</span>
                          <Badge variant="outline" className={`text-xs ${getStatusBadge(log.status)}`}>
                            {log.status}
                          </Badge>
                        </div>
                        <p className="text-sm font-medium text-slate-800 truncate">{log.message_type}</p>
                        {log.customer_email && (
                          <p className="text-xs text-slate-500">To: {log.customer_email}</p>
                        )}
                        {expandedId !== log.id && (
                          <p className="text-xs text-slate-400 line-clamp-1 mt-1">{log.content?.substring(0, 120)}...</p>
                        )}
                      </div>
                      <div className="flex flex-col items-end gap-2 flex-shrink-0">
                        <p className="text-xs text-slate-400 whitespace-nowrap">
                          {new Date(log.sent_at).toLocaleDateString()} {new Date(log.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                        <div className="flex items-center gap-1">
                          {expandedId === log.id ? (
                            <ChevronUp className="w-4 h-4 text-slate-400" />
                          ) : (
                            <ChevronDown className="w-4 h-4 text-slate-400" />
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Expanded Email Preview */}
                  {expandedId === log.id && (
                    <div className="border-t bg-slate-50 p-4" data-testid={`email-preview-${log.id}`}>
                      <div className="mb-3 flex items-center justify-between">
                        <div>
                          <p className="text-xs text-slate-500"><strong>To:</strong> {log.customer_email || 'N/A'}</p>
                          <p className="text-xs text-slate-500"><strong>Subject:</strong> {log.message_type}</p>
                          <p className="text-xs text-slate-500"><strong>Sent:</strong> {new Date(log.sent_at).toLocaleString()}</p>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => { e.stopPropagation(); navigate(`/customers/${log.customer_id}`); }}
                          data-testid={`view-customer-${log.id}`}
                        >
                          <ExternalLink className="w-3 h-3 mr-1" />
                          View Customer
                        </Button>
                      </div>
                      <div className="bg-white border rounded-lg p-4 text-sm text-slate-700 whitespace-pre-wrap max-h-64 overflow-y-auto">
                        {log.content || 'No content available'}
                      </div>
                    </div>
                  )}
                </div>
              ))}
              
              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between pt-4">
                  <p className="text-sm text-slate-500">
                    Page {page} of {totalPages}
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={page <= 1}
                      onClick={() => setPage(p => p - 1)}
                      data-testid="email-prev-page"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={page >= totalPages}
                      onClick={() => setPage(p => p + 1)}
                      data-testid="email-next-page"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12 text-slate-500">
              <Mail className="w-12 h-12 mx-auto mb-4 text-slate-300" />
              <p>No emails found</p>
              <p className="text-xs mt-1">Emails sent from customer profiles will appear here</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default EmailLogsPage;
