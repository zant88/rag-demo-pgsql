import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface KnowledgeEntry {
  id: number;
  title: string;
  summary: string;
  content: string;
  keywords: string[];
  categories: string[];
  source?: string;
  author?: string;
  date?: string;
  created_at?: string;
}

const KnowledgeList: React.FC = () => {
  const [entries, setEntries] = useState<KnowledgeEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const fetchEntries = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await axios.get('/api/v1/knowledge/entries');
      setEntries(res.data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to fetch entries.');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchEntries();
  }, []);

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this entry?')) return;
    setDeletingId(id);
    try {
      await axios.delete(`/api/v1/knowledge/entry/${id}`);
      setEntries(entries => entries.filter(e => e.id !== id));
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Delete failed.');
    }
    setDeletingId(null);
  };

  if (loading) return <div>Loading knowledge entries...</div>;
  if (error) return <div className="text-red-600">{error}</div>;

  return (
    <div className="space-y-4">
      {entries.length === 0 ? (
        <div>No manual knowledge entries found.</div>
      ) : (
        entries.map(entry => (
          <div key={entry.id} className="border rounded p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-3 bg-white shadow">
            <div>
              <div className="font-bold text-lg">{entry.title}</div>
              <div className="text-sm text-gray-700">{entry.summary}</div>
              <div className="mt-1 text-xs text-gray-500">
                {entry.author && <span>By {entry.author}. </span>}
                {entry.date && <span>{entry.date}. </span>}
                {entry.categories && entry.categories.length > 0 && (
                  <span>Categories: {entry.categories.join(', ')}. </span>
                )}
                {entry.keywords && entry.keywords.length > 0 && (
                  <span>Keywords: {entry.keywords.join(', ')}</span>
                )}
              </div>
            </div>
            <button
              className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 disabled:opacity-60"
              onClick={() => handleDelete(entry.id)}
              disabled={deletingId === entry.id}
            >
              {deletingId === entry.id ? 'Deleting...' : 'Delete'}
            </button>
          </div>
        ))
      )}
    </div>
  );
};

export default KnowledgeList;
