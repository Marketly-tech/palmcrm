import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Card, CardContent } from "../ui/card";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "../ui/select";
import { Search, Filter, AlertTriangle, Building2 } from "lucide-react";

const CustomerFilters = ({
  search, setSearch, projectFilter, setProjectFilter,
  statusFilter, setStatusFilter, agreementFilter, setAgreementFilter,
  bankFilter, setBankFilter, banks,
  projects, total,
}) => (
  <Card>
    <CardContent className="p-4">
      <div className="flex flex-col gap-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input placeholder="Search by name, email, phone, or ID..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10" data-testid="search-customers-input" />
          </div>
          <Select value={projectFilter || "all"} onValueChange={(v) => setProjectFilter(v === "all" ? "" : v)}>
            <SelectTrigger className="w-full sm:w-48" data-testid="filter-project-select">
              <Filter className="w-4 h-4 mr-2" /><SelectValue placeholder="All Projects" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Projects</SelectItem>
              {projects.map((project) => (
                <SelectItem key={project.name} value={project.name}>{project.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={bankFilter || "all"} onValueChange={(v) => setBankFilter(v === "all" ? "" : v)}>
            <SelectTrigger className={`w-full sm:w-48 ${bankFilter ? "border-amber-400 bg-amber-50" : ""}`} data-testid="filter-bank-select">
              <Building2 className="w-4 h-4 mr-2" /><SelectValue placeholder="All Banks" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Banks</SelectItem>
              {(banks || []).map((bank) => (
                <SelectItem key={bank} value={bank}>{bank}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={statusFilter || "all"} onValueChange={(v) => setStatusFilter(v === "all" ? "" : v)}>
            <SelectTrigger className="w-full sm:w-48" data-testid="filter-status-select"><SelectValue placeholder="All Status" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="draft">Draft</SelectItem>
              <SelectItem value="sent">Sent</SelectItem>
              <SelectItem value="signed">Signed</SelectItem>
              <SelectItem value="disbursement">Disbursement</SelectItem>
            </SelectContent>
          </Select>
          <Select value={agreementFilter || "all"} onValueChange={(v) => setAgreementFilter(v === "all" ? "" : v)}>
            <SelectTrigger className="w-full sm:w-52" data-testid="filter-agreement-select"><SelectValue placeholder="Agreement Filter" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Agreements</SelectItem>
              <SelectItem value="upcoming_due">Upcoming Due (Next 5 Days)</SelectItem>
              <SelectItem value="pending_agreement">Pending Agreement</SelectItem>
              <SelectItem value="overdue">Disbursement Overdue</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant={agreementFilter === "overdue" ? "default" : "outline"} size="sm"
            onClick={() => setAgreementFilter(agreementFilter === "overdue" ? "" : "overdue")}
            className={agreementFilter === "overdue" ? "bg-red-600 hover:bg-red-700" : "border-red-300 text-red-600 hover:bg-red-50"}
            data-testid="filter-overdue-btn"
          >
            <AlertTriangle className="w-4 h-4 mr-2" />
            Disbursement Overdue
            {agreementFilter === "overdue" && <Badge variant="secondary" className="ml-2 bg-white text-red-600">{total}</Badge>}
          </Button>
          {agreementFilter === "overdue" && (
            <span className="text-sm text-slate-500">Showing customers with pending payments as per current disbursement slab</span>
          )}
        </div>
      </div>
    </CardContent>
  </Card>
);

export default CustomerFilters;
