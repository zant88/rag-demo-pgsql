import Head from 'next/head';
import ChatInterface from '../components/ChatInterface';

export default function ChatPage() {
  return (
    <>
      <Head>
        <title>Chat - Agentic RAG Knowledge App</title>
      </Head>
      <main className="min-h-screen flex flex-col p-4">
        <h1 className="text-3xl font-bold mb-6 text-center">Chat with Knowledge Base</h1>
        <div className="w-full max-w-2xl mx-auto flex-1 flex flex-col">
          <ChatInterface />
        </div>
      </main>
    </>
  );
}
