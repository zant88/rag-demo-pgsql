import React, { useState, useRef, useEffect } from 'react';
// If you see a uuid module error, run: npm install uuid
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';
import { ArrowUpTrayIcon } from '@heroicons/react/24/outline';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

interface UploadStatus {
  progress: number;
  status: 'idle' | 'uploading' | 'assembling' | 'completed' | 'error';
  message?: string;
}

const CHUNK_SIZE = 5 * 1024 * 1024; // 5MB

const UploadArea: React.FC = () => {
  const [clientId] = useState(() => uuidv4());
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [processingMsg, setProcessingMsg] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<UploadStatus>({ progress: 0, status: 'idle' });
  const [uploadedDocId, setUploadedDocId] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Open WebSocket connection on mount
    const socket = new WebSocket(`ws://localhost:8000/api/v1/ws/processing/${clientId}`);
    socket.onopen = () => console.log('WebSocket connected');
    socket.onclose = () => console.log('WebSocket disconnected');
    socket.onerror = (e) => console.error('WebSocket error', e);
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.event === 'processing_complete') {
          setProcessingMsg(`Document "${data.filename}" (ID: ${data.document_id}) has finished processing and is ready!`);
          setStatus(s => ({ ...s, status: 'completed', message: 'Processing complete!' }));
          toast.success(`Document "${data.filename}" is ready!`, { position: 'top-right', autoClose: 6000 });
        }
      } catch {}
    };
    setWs(socket);
    return () => { socket.close(); };
  }, [clientId]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setStatus({ progress: 0, status: 'idle' });
      setUploadedDocId(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setStatus({ progress: 0, status: 'uploading' });
    if (file.size <= CHUNK_SIZE) {
      // Small file, upload directly
      const formData = new FormData();
      formData.append('file', file);
      // Pass client_id to backend for notification
      formData.append('client_id', clientId);
      try {
        const res = await axios.post('/api/v1/documents/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        setStatus({ progress: 100, status: 'completed', message: 'Upload complete!' });
        setUploadedDocId(res.data.id);
      } catch (err: any) {
        setStatus({ progress: 0, status: 'error', message: err?.response?.data?.detail || 'Upload failed.' });
      }
      return;
    }
    // Large file, upload in chunks
    const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
    let documentId = '';
    for (let i = 0; i < totalChunks; i++) {
      const start = i * CHUNK_SIZE;
      const end = Math.min(start + CHUNK_SIZE, file.size);
      const chunk = file.slice(start, end);
      const chunkForm = new FormData();
      chunkForm.append('file_chunk', chunk);
      chunkForm.append('document_id', documentId || 'new');
      chunkForm.append('chunk_index', String(i));
      chunkForm.append('total_chunks', String(totalChunks));
      chunkForm.append('filename', file.name);
      // Pass client_id to backend for notification (only on first chunk)
      if (i === 0) chunkForm.append('client_id', clientId);
      try {
        const res = await axios.post('/api/v1/documents/upload-chunked', chunkForm, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        documentId = res.data.document_id || documentId;
        setStatus({ progress: Math.round(((i + 1) / totalChunks) * 100), status: 'uploading', message: `Chunk ${i + 1} uploaded` });
        if (i === totalChunks - 1) {
          setStatus({ progress: 100, status: 'assembling', message: 'Assembling and processing...' });
        }
      } catch (err: any) {
        setStatus({ progress: Math.round(((i + 1) / totalChunks) * 100), status: 'error', message: err?.response?.data?.detail || 'Chunk upload failed.' });
        break;
      }
    }
    setUploadedDocId(documentId);
    setStatus({ progress: 100, status: 'completed', message: 'Upload complete!' });
  };

  return (
    <div className="bg-white rounded-lg shadow p-4 flex flex-col gap-4">
      <input
        type="file"
        ref={inputRef}
        className="hidden"
        onChange={handleFileChange}
        accept=".pdf,.doc,.docx,.png,.jpg,.jpeg,.txt"
      />
      {processingMsg && (
        <div className="text-xs text-green-700 font-semibold mt-2">{processingMsg}</div>
      )}
      <button
        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        onClick={() => inputRef.current?.click()}
      >
        <ArrowUpTrayIcon className="h-5 w-5" />
        Select File
      </button>
      {file && (
        <div className="flex flex-col gap-2">
          <div className="text-sm font-medium">{file.name} ({Math.round(file.size / 1024)} KB)</div>
          <button
            className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
            onClick={handleUpload}
            disabled={status.status === 'uploading' || status.status === 'assembling'}
          >
            {status.status === 'uploading' ? 'Uploading...' : status.status === 'assembling' ? 'Processing...' : 'Upload'}
          </button>
          <div className="w-full bg-gray-200 rounded h-2">
            <div
              className="bg-blue-500 h-2 rounded"
              style={{ width: `${status.progress}%` }}
            ></div>
          </div>
          {status.message && <div className={`text-xs ${status.status === 'error' ? 'text-red-600' : 'text-green-700'}`}>{status.message}</div>}
        </div>
      )}
      {uploadedDocId && (
        <div className="text-xs text-green-700">Document uploaded! ID: {uploadedDocId}</div>
      )}
      <ToastContainer />
    </div>
  );
};

export default UploadArea;
