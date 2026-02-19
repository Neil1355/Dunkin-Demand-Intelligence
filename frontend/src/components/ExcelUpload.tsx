import React, { useState } from 'react';
import { Upload, FileSpreadsheet, CheckCircle2, AlertCircle } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'https://dunkin-demand-intelligence.onrender.com/api/v1';

export default function ExcelUpload() {
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const uploadFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
      setError('Please upload an Excel file (.xlsx or .xls)');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/excel/upload`, {
        method: "POST",
        body: formData,
        credentials: 'include', // Send auth cookies
      });

      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.error || 'Upload failed');
      }

      setSuccess(`Successfully imported ${data.inserted || 0} records!`);
      // Clear the file input
      e.target.value = '';
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Upload failed';
      setError(errorMsg);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* File Upload */}
      <div className="flex items-center gap-4">
        <label 
          className="flex items-center gap-2 px-6 py-3 rounded-full cursor-pointer transition-all hover:scale-105 shadow-md text-white"
          style={{ backgroundColor: '#FF671F' }}
        >
          <Upload size={18} />
          {uploading ? 'Uploading...' : 'Upload Excel File'}
          <input
            type="file"
            accept=".xlsx,.xls"
            onChange={uploadFile}
            disabled={uploading}
            className="hidden"
          />
        </label>
        <FileSpreadsheet size={24} style={{ color: '#8B7355' }} />
      </div>

      {/* Success Message */}
      {success && (
        <div className="flex items-center gap-2 p-4 rounded-2xl" style={{ backgroundColor: '#E8F5E9', color: '#2E7D32' }}>
          <CheckCircle2 size={20} />
          <span>{success}</span>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="flex items-center gap-2 p-4 rounded-2xl" style={{ backgroundColor: '#FFEBEE', color: '#C62828' }}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Instructions */}
      <div className="p-4 rounded-2xl text-sm" style={{ backgroundColor: '#FFF8F0', color: '#8B7355' }}>
        <p className="font-semibold mb-2">Excel Format Requirements:</p>
        <ul className="list-disc list-inside space-y-1">
          <li>Columns: <code>store_id</code>, <code>product_id</code>, <code>date</code></li>
          <li>Optional: <code>produced</code>, <code>waste</code></li>
          <li>Date format: YYYY-MM-DD</li>
        </ul>
      </div>
    </div>
  );
}
