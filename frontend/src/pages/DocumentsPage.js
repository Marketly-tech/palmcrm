import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Textarea } from "../components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../components/ui/dialog";
import { toast } from "sonner";
import {
  FileText,
  Plus,
  Loader2,
  Download,
  Edit,
  Save,
  File,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DocumentsPage = () => {
  const [templates, setTemplates] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [templateDialogOpen, setTemplateDialogOpen] = useState(false);
  const [generateDialogOpen, setGenerateDialogOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [saving, setSaving] = useState(false);

  const [newTemplate, setNewTemplate] = useState({
    name: "",
    doc_type: "",
    content: "",
  });

  const [generateForm, setGenerateForm] = useState({
    customer_id: "",
    doc_type: "",
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [templatesRes, customersRes] = await Promise.all([
        axios.get(`${API}/templates`),
        axios.get(`${API}/customers`),
      ]);
      setTemplates(templatesRes.data);
      setCustomers(customersRes.data.customers);
    } catch (error) {
      toast.error("Failed to fetch data");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTemplate = async () => {
    if (!newTemplate.name || !newTemplate.doc_type || !newTemplate.content) {
      toast.error("Please fill all fields");
      return;
    }

    setSaving(true);
    try {
      await axios.post(`${API}/templates`, newTemplate);
      fetchData();
      setTemplateDialogOpen(false);
      setNewTemplate({ name: "", doc_type: "", content: "" });
      toast.success("Template created successfully");
    } catch (error) {
      toast.error("Failed to create template");
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateTemplate = async () => {
    if (!editingTemplate) return;

    setSaving(true);
    try {
      await axios.put(`${API}/templates/${editingTemplate.id}`, {
        name: editingTemplate.name,
        content: editingTemplate.content,
      });
      fetchData();
      setEditingTemplate(null);
      toast.success("Template updated successfully");
    } catch (error) {
      toast.error("Failed to update template");
    } finally {
      setSaving(false);
    }
  };

  const handleGenerateDocument = async () => {
    if (!generateForm.customer_id || !generateForm.doc_type) {
      toast.error("Please select customer and document type");
      return;
    }

    setSaving(true);
    try {
      await axios.post(`${API}/documents/generate`, {
        customer_id: generateForm.customer_id,
        doc_type: generateForm.doc_type,
      });
      setGenerateDialogOpen(false);
      setGenerateForm({ customer_id: "", doc_type: "" });
      toast.success("Document generated successfully");
    } catch (error) {
      toast.error("Failed to generate document");
    } finally {
      setSaving(false);
    }
  };

  const getDocTypeBadge = (type) => {
    const styles = {
      sales_agreement: "bg-blue-100 text-blue-700",
      allotment_letter: "bg-green-100 text-green-700",
    };
    return styles[type] || "bg-slate-100 text-slate-700";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="documents-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="font-heading text-3xl font-bold text-slate-900">Documents</h1>
          <p className="text-slate-500 mt-1">Manage document templates and generate documents</p>
        </div>
        <div className="flex gap-2">
          <Dialog open={generateDialogOpen} onOpenChange={setGenerateDialogOpen}>
            <DialogTrigger asChild>
              <Button data-testid="generate-document-btn">
                <FileText className="w-4 h-4 mr-2" />
                Generate Document
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Generate Document</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label>Select Customer</Label>
                  <Select
                    value={generateForm.customer_id}
                    onValueChange={(value) => setGenerateForm({ ...generateForm, customer_id: value })}
                  >
                    <SelectTrigger data-testid="select-customer">
                      <SelectValue placeholder="Select a customer" />
                    </SelectTrigger>
                    <SelectContent>
                      {customers.map((customer) => (
                        <SelectItem key={customer.id} value={customer.id}>
                          {customer.name} - {customer.customer_id}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Document Type</Label>
                  <Select
                    value={generateForm.doc_type}
                    onValueChange={(value) => setGenerateForm({ ...generateForm, doc_type: value })}
                  >
                    <SelectTrigger data-testid="select-doc-type">
                      <SelectValue placeholder="Select document type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="sales_agreement">Sales Agreement</SelectItem>
                      <SelectItem value="allotment_letter">Allotment Letter</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button
                  onClick={handleGenerateDocument}
                  className="w-full"
                  disabled={saving}
                  data-testid="confirm-generate-btn"
                >
                  {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                  Generate Document
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Tabs defaultValue="templates" className="space-y-4">
        <TabsList>
          <TabsTrigger value="templates" data-testid="tab-templates">
            <File className="w-4 h-4 mr-2" />
            Templates
          </TabsTrigger>
        </TabsList>

        {/* Templates Tab */}
        <TabsContent value="templates">
          <div className="flex justify-end mb-4">
            <Dialog open={templateDialogOpen} onOpenChange={setTemplateDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="outline" data-testid="create-template-btn">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Template
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Create Document Template</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label>Template Name</Label>
                    <Input
                      value={newTemplate.name}
                      onChange={(e) => setNewTemplate({ ...newTemplate, name: e.target.value })}
                      placeholder="e.g., Standard Sales Agreement"
                      data-testid="template-name-input"
                    />
                  </div>
                  <div>
                    <Label>Document Type</Label>
                    <Select
                      value={newTemplate.doc_type}
                      onValueChange={(value) => setNewTemplate({ ...newTemplate, doc_type: value })}
                    >
                      <SelectTrigger data-testid="template-type-select">
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="sales_agreement">Sales Agreement</SelectItem>
                        <SelectItem value="allotment_letter">Allotment Letter</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Template Content</Label>
                    <p className="text-xs text-slate-500 mb-2">
                      Use placeholders like {"{customer_name}"}, {"{unit_number}"}, {"{project}"}, {"{total_price}"}, etc.
                    </p>
                    <Textarea
                      value={newTemplate.content}
                      onChange={(e) => setNewTemplate({ ...newTemplate, content: e.target.value })}
                      placeholder="Enter template content with placeholders..."
                      rows={10}
                      className="font-mono text-sm"
                      data-testid="template-content-input"
                    />
                  </div>
                  <Button
                    onClick={handleCreateTemplate}
                    className="w-full"
                    disabled={saving}
                    data-testid="save-template-btn"
                  >
                    {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                    Create Template
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          {/* Default Templates Info */}
          <Card className="mb-6 bg-blue-50 border-blue-200">
            <CardContent className="p-4">
              <p className="text-sm text-blue-700">
                <strong>Note:</strong> Default templates are available for Sales Agreement and Allotment Letter.
                Create custom templates to override the defaults.
              </p>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Default Templates */}
            {["sales_agreement", "allotment_letter"].map((type) => {
              const customTemplate = templates.find((t) => t.doc_type === type);
              return (
                <Card key={type} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <Badge className={getDocTypeBadge(type)}>
                        {type.replace(/_/g, " ").toUpperCase()}
                      </Badge>
                      {customTemplate && (
                        <Badge variant="outline" className="text-xs">Custom</Badge>
                      )}
                    </div>
                    <CardTitle className="text-lg capitalize mt-2">
                      {customTemplate?.name || type.replace(/_/g, " ")}
                    </CardTitle>
                    <CardDescription>
                      {customTemplate ? "Custom template" : "Default template"}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {customTemplate && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setEditingTemplate(customTemplate)}
                        data-testid={`edit-template-${type}`}
                      >
                        <Edit className="w-4 h-4 mr-2" />
                        Edit
                      </Button>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Edit Template Dialog */}
          {editingTemplate && (
            <Dialog open={!!editingTemplate} onOpenChange={() => setEditingTemplate(null)}>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Edit Template</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label>Template Name</Label>
                    <Input
                      value={editingTemplate.name}
                      onChange={(e) =>
                        setEditingTemplate({ ...editingTemplate, name: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <Label>Template Content</Label>
                    <Textarea
                      value={editingTemplate.content}
                      onChange={(e) =>
                        setEditingTemplate({ ...editingTemplate, content: e.target.value })
                      }
                      rows={12}
                      className="font-mono text-sm"
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" onClick={() => setEditingTemplate(null)} className="flex-1">
                      Cancel
                    </Button>
                    <Button onClick={handleUpdateTemplate} className="flex-1" disabled={saving}>
                      {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                      Save Changes
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DocumentsPage;
