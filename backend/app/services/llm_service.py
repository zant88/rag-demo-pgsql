# import requests  # For Ollama (commented out)
import groq
from app.core.config import settings

class LLMService:
    def __init__(self):
        # Groq configuration
        self.client = groq.Groq(
            api_key=settings.GROQ_API_KEY
        )
        self.model = "llama3-8b-8192"  # or "mixtral-8x7b-32768", "llama3-70b-8192"
        
        # Ollama configuration (commented out for local use)
        # self.model = "llama3"

    async def generate_response(self, query: str, context: str) -> str:
        try:
            # Use Groq direct API
            messages = [
                {
                    "role": "system",
                    "content": self._get_system_preamble()
                },
                {
                    "role": "user",
                    "content": self._build_rag_prompt(query, context)
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=1024
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating LLM response: {str(e)}")
            return f"I apologize, but I encountered an error while generating a response: {str(e)}"
        
        # Ollama implementation (commented out for local use)
        # try:
        #     prompt = self._build_rag_prompt(query, context)
        #     response = requests.post(
        #         "http://localhost:11434/api/chat",
        #         json={
        #             "model": self.model,
        #             "messages": [
        #                 {"role": "system", "content": self._get_system_preamble()},
        #                 {"role": "user", "content": prompt}
        #             ]
        #         }
        #     )
        #     response.raise_for_status()
        #     # Ollama sometimes returns multi-line JSON or streaming JSON objects
        #     raw_text = response.text.strip()
        #     import json
        #     assistant_contents = []
        #     for line in raw_text.splitlines():
        #         try:
        #             obj = json.loads(line)
        #             # Ollama streaming: each line has obj['message'] with role/content
        #             msg = obj.get("message", {})
        #             if msg.get("role") == "assistant":
        #                 assistant_contents.append(msg.get("content", ""))
        #         except Exception:
        #             continue
        #     if not assistant_contents:
        #         raise ValueError("No assistant content found in Ollama response")
        #     return "".join(assistant_contents)
        # except Exception as e:
        #     print(f"Error generating LLM response: {str(e)}")
        #     return f"I apologize, but I encountered an error while generating a response: {str(e)}"

    def _build_rag_prompt(self, query: str, context: str) -> str:
        prompt = f"""Based on the following context from the knowledge base, please answer the user's question. 

Context:
{context}

User Question: {query}

Please provide a comprehensive answer based on the context provided. If the context doesn't contain enough information to fully answer the question, please indicate what information is missing. Always cite the sources when providing information."""
        return prompt

    def _get_system_preamble(self) -> str:
        return """🚨 MANDATORY LANGUAGE RULE - READ THIS FIRST:
BEFORE writing ANY response, you MUST:
1. Identify the language of the user's question
2. Write your ENTIRE response in that SAME language
3. If the question contains Indonesian words like "siapa", "tentang", "ceritakan", "apa", "bagaimana" → respond ENTIRELY in Bahasa Indonesia
4. If the question is in English → respond ENTIRELY in English
5. NEVER mix languages - use only ONE language throughout your entire response

You are a helpful, multilingual AI assistant designed for general-purpose knowledge-based systems. You have strong reasoning capabilities, can understand synonyms and rephrased questions using semantic search, and provide accurate answers grounded in available documents.

🔹 Guidelines:
Always base responses on the provided context or retrieved documents.

If the answer is not found in the context, state this clearly and politely. Do not guess or invent information.

Cite the source of any answer you provide — include the document name and section or title if available.

Answer clearly and completely, using bullet points or numbered lists when helpful.

When asked about something outside the document scope, respond politely:
- English: "I'm sorry, I can only answer based on the information available in the documents."
- Indonesian: "Maaf, saya hanya dapat menjawab berdasarkan informasi yang tersedia dalam dokumen."

If the context includes sections like "products", "services", "scope", "layanan", or "produk", enumerate or summarize all listed items explicitly.

When relevant, provide practical, actionable insights — not just facts.

You may interpret synonyms, abbreviations, and semantic variations of terms using reasoning and context.

Stay concise, helpful, and accurate.
"""
#     def _build_rag_prompt(self, query: str, context: str) -> str:
#         prompt = f"""Based on the following context from the knowledge base, please answer the user's question. 

# Context:
# {context}

# User Question: {query}

# Please provide a comprehensive answer based on the context provided. If the context doesn't contain enough information to fully answer the question, please indicate what information is missing. Always cite the sources when providing information."""
#         return prompt

#     def _get_system_preamble(self) -> str:
#         return """You are a helpful AI assistant that answers questions based on a knowledge base of documents. 

# Guidelines:
# 1. Always base your answers on the provided context
# 2. If information is not available in the context, clearly state this
# 3. Cite sources when providing information (mention document names and sections)
# 4. Provide clear, comprehensive answers
# 5. Support both English and Indonesian languages
# 6. If asked about something not in the context, politely explain that you can only answer based on the available documents
# 7. If the context contains a section listing specific products or services (such as 'business scope', 'produk', or 'layanan'), extract and enumerate all items from that section explicitly in your answer.
# """