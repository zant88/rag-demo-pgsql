import React, { useState } from 'react';
import axios from 'axios';

const defaultForm = {
  title: '',
  summary: '',
  content: '',
  keywords: '',
  categories: '',
  source: '',
  author: '',
  date: '',
};

const KnowledgeForm: React.FC = () => {
  const [form, setForm] = useState(defaultForm);
  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('submitting');
    setMessage('');
    try {
      await axios.post('/api/v1/knowledge/manual-entry', {
        ...form,
        keywords: form.keywords.split(',').map(k => k.trim()).filter(Boolean),
        categories: form.categories.split(',').map(c => c.trim()).filter(Boolean),
      });
      setStatus('success');
      setMessage('Knowledge entry submitted!');
      setForm(defaultForm);
    } catch (err: any) {
      setStatus('error');
      setMessage(err?.response?.data?.detail || 'Submission failed.');
    }
  };

  return (
    <form className="bg-white rounded-lg shadow p-4 flex flex-col gap-3" onSubmit={handleSubmit}>
      <input name="title" placeholder="Title" value={form.title} onChange={handleChange} required className="border p-2 rounded" />
      <input name="summary" placeholder="Summary" value={form.summary} onChange={handleChange} className="border p-2 rounded" />
      <textarea name="content" placeholder="Detailed Content" value={form.content} onChange={handleChange} required rows={4} className="border p-2 rounded" />
      <input name="keywords" placeholder="Keywords (comma-separated)" value={form.keywords} onChange={handleChange} className="border p-2 rounded" />
      <input name="categories" placeholder="Categories (comma-separated)" value={form.categories} onChange={handleChange} className="border p-2 rounded" />
      <input name="source" placeholder="Source" value={form.source} onChange={handleChange} className="border p-2 rounded" />
      <input name="author" placeholder="Author" value={form.author} onChange={handleChange} className="border p-2 rounded" />
      <input name="date" placeholder="Date" value={form.date} onChange={handleChange} className="border p-2 rounded" />
      <button
        type="submit"
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-60"
        disabled={status === 'submitting'}
      >
        {status === 'submitting' ? 'Submitting...' : 'Submit'}
      </button>
      {message && <div className={`text-xs ${status === 'error' ? 'text-red-600' : 'text-green-700'}`}>{message}</div>}
    </form>
  );
};

export default KnowledgeForm;
