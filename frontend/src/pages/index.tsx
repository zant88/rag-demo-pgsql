import Head from 'next/head';
import UploadArea from '../components/UploadArea';
import ChatInterface from '../components/ChatInterface';
import KnowledgeForm from '../components/KnowledgeForm';

export default function Home() {
  return (
    <>
      <Head>
        <title>Agentic RAG Knowledge App</title>
        <meta name="description" content="RAG-based knowledge app with smart upload and semantic search" />
      </Head>
      <main className="min-h-screen flex flex-col items-center justify-center p-4 max-w-4xl mx-auto">
        <h1 className="text-4xl font-extrabold text-blue-700 text-center mb-4 mt-16">Welcome to the Agentic RAG Knowledge App</h1>
        <p className="text-lg text-gray-700 text-center mb-8">Upload documents, input knowledge, and chat with your knowledge base using the navigation above.</p>
        <div className="flex gap-4">
          <a href="/upload" className="bg-blue-500 text-white px-6 py-3 rounded shadow hover:bg-blue-600 transition">Go to Document Upload</a>
          <a href="/manual" className="bg-green-500 text-white px-6 py-3 rounded shadow hover:bg-green-600 transition">Manual Knowledge Input</a>
          <a href="/chat" className="bg-purple-500 text-white px-6 py-3 rounded shadow hover:bg-purple-600 transition">Chat</a>
        </div>
      </main>
    </>
  );
}
