# Agentic RAG Knowledge App Frontend

This is the frontend for the Agentic RAG-based Knowledge App. It is built with Next.js and Tailwind CSS.

## Features
- Resumable, chunked document upload with status
- Manual knowledge entry form
- Chat interface with source citations

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```
2. Run the development server:
   ```bash
   npm run dev
   ```
3. The app will be available at [http://localhost:3000](http://localhost:3000)

## Configuration
- The frontend proxies API requests to the FastAPI backend running on port 8000.
- Update `next.config.js` if your backend runs on a different port.
