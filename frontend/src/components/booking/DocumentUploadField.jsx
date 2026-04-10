import { Button } from "../ui/button";
import { Label } from "../ui/label";
import { Upload, Camera, FileText, X } from "lucide-react";

const DocumentUploadField = ({ label, fileType, fileRef, cameraRef, uploadedFile, onUpload, onRemove }) => {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <input
        type="file"
        ref={fileRef}
        className="hidden"
        accept="image/*,.pdf"
        onChange={(e) => onUpload(fileType, e.target.files[0])}
      />
      <input
        type="file"
        ref={cameraRef}
        className="hidden"
        accept="image/*"
        capture="environment"
        onChange={(e) => onUpload(fileType, e.target.files[0])}
      />
      {uploadedFile ? (
        <div className="flex items-center gap-2 p-2 bg-green-50 border border-green-200 rounded">
          <FileText className="w-4 h-4 text-green-600" />
          <span className="text-sm truncate flex-1">{uploadedFile.name}</span>
          <Button type="button" variant="ghost" size="sm" onClick={() => onRemove(fileType)}>
            <X className="w-4 h-4" />
          </Button>
        </div>
      ) : (
        <div className="flex gap-2">
          <Button
            type="button"
            variant="outline"
            className="flex-1"
            onClick={() => fileRef.current?.click()}
            data-testid={`${fileType}-upload-btn`}
          >
            <Upload className="w-4 h-4 mr-1" /> Upload
          </Button>
          <Button
            type="button"
            variant="outline"
            className="flex-1 bg-blue-50 border-blue-200 hover:bg-blue-100 text-blue-700"
            onClick={() => cameraRef.current?.click()}
            data-testid={`${fileType}-camera-btn`}
          >
            <Camera className="w-4 h-4 mr-1" /> Camera
          </Button>
        </div>
      )}
    </div>
  );
};

export default DocumentUploadField;
