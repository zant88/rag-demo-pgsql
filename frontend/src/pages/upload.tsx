import Head from 'next/head';
import UploadArea from '../components/UploadArea';

export default function UploadPage() {
  return (
    <>
      <Head>
        <title>Upload Document - Agentic RAG Knowledge App</title>
      </Head>
      <main className="min-h-screen flex flex-col items-center justify-center p-4">
        <h1 className="text-3xl font-bold mb-6">Document Upload</h1>
        <div className="w-full max-w-2xl">
          <UploadArea />
        </div>
      </main>
    </>
  );
}
