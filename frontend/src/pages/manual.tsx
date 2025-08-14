import Head from 'next/head';
import KnowledgeForm from '../components/KnowledgeForm';
import KnowledgeList from '../components/KnowledgeList';

export default function ManualKnowledgePage() {
  return (
    <>
      <Head>
        <title>Manual Knowledge Input - Agentic RAG Knowledge App</title>
      </Head>
      <main className="min-h-screen flex flex-col items-center justify-center p-4">
        <h1 className="text-3xl font-bold mb-6">Manual Knowledge Input</h1>
        <div className="w-full max-w-2xl space-y-10">
          <KnowledgeForm />
          <hr className="my-4" />
          <h2 className="text-xl font-semibold mb-2">Manual Knowledge Entries</h2>
          <KnowledgeList />
        </div>
      </main>
    </>
  );
}
