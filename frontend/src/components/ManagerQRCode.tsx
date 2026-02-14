import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { AlertCircle, Download, RefreshCw, Loader2, CheckCircle2 } from 'lucide-react';
import { Alert, AlertDescription } from './ui/alert';

const API_BASE = import.meta.env.VITE_API_URL || "https://dunkin-demand-intelligence.onrender.com/api/v1";

interface QRCodeResponse {
  store_id: number;
  qr_base64: string;
  qr_url: string;
  status: 'existing' | 'created' | 'regenerated';
  message?: string;
}

interface QRStatusResponse {
  store_id: number;
  exists: boolean;
  created_at?: string;
  updated_at?: string;
}

export const ManagerQRCode: React.FC<{ storeId: number }> = ({ storeId }) => {
  const [qrCode, setQrCode] = useState<QRCodeResponse | null>(null);
  const [qrStatus, setQrStatus] = useState<QRStatusResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Fetch or create QR code on component mount
  useEffect(() => {
    fetchQRCode();
  }, [storeId]);

  const fetchQRCode = async () => {
    setLoading(true);
    setError(null);
    setSuccessMessage(null);
    try {
      const url = `${API_BASE}/qr/store/${storeId}`;
      console.log('Fetching QR from:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      console.log('QR Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('QR Error response:', errorText);
        throw new Error(`Failed to fetch QR code: ${response.status} ${response.statusText}`);
      }

      const data: QRCodeResponse = await response.json();
      setQrCode(data);
      
      setSuccessMessage(`QR Code ${data.status === 'created' ? 'created' : 'loaded'} successfully`);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to fetch QR code';
      console.error('QR Fetch Error:', err);
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const checkQRStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/qr/status/${storeId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) throw new Error('Failed to check status');

      const data: QRStatusResponse = await response.json();
      setQrStatus(data);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to check status';
      setError(errorMsg);
    }
  };

  const downloadQR = async (withHeader: boolean = true) => {
    setDownloading(true);
    setError(null);
    setSuccessMessage(null);
    try {
      const endpoint = withHeader 
        ? `${API_BASE}/qr/download/${storeId}` 
        : `${API_BASE}/qr/download/${storeId}/simple`;

      const response = await fetch(endpoint, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error('Failed to download QR code');
      }

      // Create blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `waste_qr_store_${storeId}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setSuccessMessage('QR code downloaded successfully');
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Download failed';
      setError(errorMsg);
    } finally {
      setDownloading(false);
    }
  };

  const regenerateQR = async () => {
    if (!confirm('Regenerate QR code? This will create a new code for scanning.')) {
      return;
    }

    setLoading(true);
    setError(null);
    setSuccessMessage(null);
    try {
      const response = await fetch(`${API_BASE}/qr/regenerate/${storeId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        throw new Error('Failed to regenerate QR code');
      }

      const data: QRCodeResponse = await response.json();
      setQrCode(data);

      setSuccessMessage('QR code regenerated successfully');
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Regeneration failed';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Waste Submission QR Code</CardTitle>
          <CardDescription>
            Create and manage QR code for Store #{storeId}
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Success Message */}
          {successMessage && (
            <Alert className="bg-green-50 border-green-200">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">
                {successMessage}
              </AlertDescription>
            </Alert>
          )}

          {/* Error State */}
          {error && (
            <Alert className="bg-red-50 border-red-200">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">
                {error}
              </AlertDescription>
            </Alert>
          )}

          {/* QR Code Display */}
          {qrCode && (
            <div className="space-y-3">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 bg-gray-50 flex justify-center">
                <img
                  src={`data:image/png;base64,${qrCode.qr_base64}`}
                  alt={`QR Code for Store ${storeId}`}
                  className="w-64 h-64 object-contain"
                />
              </div>

              <div className="text-xs text-gray-600 space-y-1">
                <p>
                  <span className="font-semibold">Status:</span> {qrCode.status}
                </p>
                <p>
                  <span className="font-semibold">Target URL:</span>
                  <br />
                  <code className="text-gray-700 break-all">{qrCode.qr_url}</code>
                </p>
              </div>
            </div>
          )}

          {/* Status Info */}
          {qrStatus && (
            <div className="text-xs text-gray-600 bg-blue-50 border border-blue-200 rounded p-2">
              <p>
                <span className="font-semibold">Active:</span> {qrStatus.exists ? 'Yes' : 'No'}
              </p>
              {qrStatus.created_at && (
                <p>
                  <span className="font-semibold">Created:</span>{' '}
                  {new Date(qrStatus.created_at).toLocaleDateString()}
                </p>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className="space-y-2">
            {/* Initial Create Button */}
            {!qrCode && !loading && (
              <Button
                onClick={fetchQRCode}
                className="w-full"
                variant="default"
              >
                Create QR Code
              </Button>
            )}

            {/* Download Buttons */}
            {qrCode && (
              <>
                <Button
                  onClick={() => downloadQR(true)}
                  disabled={downloading}
                  className="w-full"
                  variant="default"
                >
                  {downloading ? (
                    <>
                      <Loader2 className="mr-2 w-4 h-4 animate-spin" />
                      Downloading...
                    </>
                  ) : (
                    <>
                      <Download className="mr-2 w-4 h-4" />
                      Download with Header
                    </>
                  )}
                </Button>

                <Button
                  onClick={() => downloadQR(false)}
                  disabled={downloading}
                  className="w-full"
                  variant="outline"
                >
                  {downloading ? (
                    <>
                      <Loader2 className="mr-2 w-4 h-4 animate-spin" />
                      Downloading...
                    </>
                  ) : (
                    <>
                      <Download className="mr-2 w-4 h-4" />
                      Download QR Only
                    </>
                  )}
                </Button>

                {/* Utility Buttons */}
                <div className="flex gap-2">
                  <Button
                    onClick={checkQRStatus}
                    className="flex-1"
                    variant="outline"
                    size="sm"
                  >
                    Check Status
                  </Button>

                  <Button
                    onClick={regenerateQR}
                    disabled={loading}
                    className="flex-1"
                    variant="outline"
                    size="sm"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-1 w-3 h-3 animate-spin" />
                        Regenerating...
                      </>
                    ) : (
                      <>
                        <RefreshCw className="mr-1 w-3 h-3" />
                        Regenerate
                      </>
                    )}
                  </Button>
                </div>
              </>
            )}

            {/* Loading State */}
            {loading && !qrCode && (
              <Button disabled className="w-full">
                <Loader2 className="mr-2 w-4 h-4 animate-spin" />
                Creating QR Code...
              </Button>
            )}
          </div>

          {/* Instructions */}
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded text-xs text-blue-800 space-y-2">
            <p className="font-semibold">How to Use:</p>
            <ol className="list-decimal list-inside space-y-1">
              <li>Download the QR code with header</li>
              <li>Print or display in store</li>
              <li>Employees scan to submit waste data</li>
              <li>QR will always point to: {storeId}</li>
            </ol>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ManagerQRCode;
