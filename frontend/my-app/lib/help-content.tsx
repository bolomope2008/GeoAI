import { ReactNode } from 'react'

interface HelpSection {
  title: string
  content: ReactNode
}

export const helpSections: HelpSection[] = [
  {
    title: "About GeoAI",
    content: (
      <div className="space-y-3">
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20 p-4 rounded-lg border">
          <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">What is GeoAI?</h4>
          <p className="text-sm text-gray-700 dark:text-gray-300">
            GeoAI is an intelligent document question-answering system powered by Retrieval-Augmented Generation (RAG) technology. 
            It combines the power of local AI models with your documents to provide accurate, contextual answers with source citations.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <p><strong>Author:</strong> <a href="mailto:bolomope2008@gmail.com" className="text-blue-600 hover:underline">bolomope2008@gmail.com</a></p>
            <p><strong>Version:</strong> 1.0.0</p>
          </div>
          <div>
            <p><strong>Technology:</strong> FastAPI + Next.js + Ollama</p>
            <p><strong>Privacy:</strong> 100% Local Processing</p>
          </div>
        </div>
      </div>
    )
  },
  {
    title: "🚀 Getting Started",
    content: (
      <div className="space-y-4">
        <div className="bg-green-50 dark:bg-green-950/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
          <h4 className="font-semibold text-green-900 dark:text-green-100 mb-2">Quick Start Guide</h4>
          <ol className="list-decimal pl-4 space-y-2 text-sm">
            <li><strong>Upload Documents:</strong> Use the &quot;Upload File&quot; button in the sidebar to add your documents</li>
            <li><strong>Process Documents:</strong> Click &quot;Refresh Database&quot; to analyze and index your documents</li>
            <li><strong>Start Chatting:</strong> Ask questions about your documents in natural language</li>
            <li><strong>Review Sources:</strong> Check the source citations for verification</li>
            <li><strong>Manage Database:</strong> Use &quot;Refresh Database&quot; for updates, &quot;Clear Database&quot; to start fresh (⚠️ destructive)</li>
          </ol>
        </div>
        
        <div className="bg-blue-50 dark:bg-blue-950/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
          <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">How RAG Works</h4>
          <div className="text-sm space-y-2">
            <p>1. <strong>Document Processing:</strong> Your documents are broken into chunks and converted to vectors</p>
            <p>2. <strong>Question Analysis:</strong> Your question is converted to a vector for similarity search</p>
            <p>3. <strong>Retrieval:</strong> The system finds the most relevant document chunks</p>
            <p>4. <strong>Generation:</strong> AI generates an answer using the retrieved context</p>
            <p>5. <strong>Citation:</strong> Sources are provided for transparency</p>
          </div>
        </div>
      </div>
    )
  },
  {
    title: "📁 File Management",
    content: (
      <div className="space-y-4">
        <div className="bg-yellow-50 dark:bg-yellow-950/20 p-4 rounded-lg border border-yellow-200 dark:border-yellow-800">
          <h4 className="font-semibold text-yellow-900 dark:text-yellow-100 mb-2">Supported File Formats</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                <strong>PDF Files:</strong> .pdf (with page tracking)
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                <strong>Word Documents:</strong> .docx
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <strong>Excel Files:</strong> .xlsx
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                <strong>CSV Files:</strong> .csv
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                <strong>Text Files:</strong> .txt
              </div>
            </div>
          </div>
        </div>

        <div className="bg-purple-50 dark:bg-purple-950/20 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
          <h4 className="font-semibold text-purple-900 dark:text-purple-100 mb-2">File Upload Best Practices</h4>
          <ul className="list-disc pl-4 space-y-1 text-sm">
            <li>Upload related documents together for better context</li>
            <li>Ensure documents are readable and not corrupted</li>
            <li>Large files may take longer to process</li>
            <li>Always refresh the database after uploading new files</li>
            <li>Use descriptive filenames for easier source identification</li>
            <li>Use &quot;Refresh Database&quot; to update with new files or settings</li>
            <li>Use &quot;Clear Database&quot; only when you want to remove all files (⚠️ destructive)</li>
          </ul>
        </div>

        <div className="bg-red-50 dark:bg-red-950/20 p-4 rounded-lg border border-red-200 dark:border-red-800">
          <h4 className="font-semibold text-red-900 dark:text-red-100 mb-2">⚠️ Important Notes</h4>
          <ul className="list-disc pl-4 space-y-1 text-sm">
            <li>Documents are processed locally - your data stays private</li>
            <li>Processing time depends on document size and complexity</li>
            <li>Refresh database after uploading new documents</li>
            <li>Supported languages: English (primary), other languages may work</li>
          </ul>
        </div>
      </div>
    )
  },
  {
    title: "🗄️ Database Management",
    content: (
      <div className="space-y-4">
        <div className="bg-green-50 dark:bg-green-950/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
          <h4 className="font-semibold text-green-900 dark:text-green-100 mb-2">🔄 Refresh Database</h4>
          <div className="space-y-2 text-sm">
            <p><strong>What it does:</strong></p>
            <ul className="list-disc pl-4 space-y-1">
              <li>Keeps all source files in the knowledge base</li>
              <li>Clears old vector embeddings</li>
              <li>Reprocesses all documents with current settings</li>
              <li>Rebuilds the searchable database</li>
            </ul>
            <p><strong>When to use:</strong></p>
            <ul className="list-disc pl-4 space-y-1">
              <li>After changing configuration (chunk size, embedding model, etc.)</li>
              <li>After uploading new files</li>
              <li>When the database seems inconsistent</li>
              <li>To update embeddings with new settings</li>
            </ul>
            <p className="text-green-700 dark:text-green-300 font-medium">✅ Safe operation - never deletes your source files</p>
          </div>
        </div>

        <div className="bg-red-50 dark:bg-red-950/20 p-4 rounded-lg border border-red-200 dark:border-red-800">
          <h4 className="font-semibold text-red-900 dark:text-red-100 mb-2">🗑️ Clear Database</h4>
          <div className="space-y-2 text-sm">
            <p><strong>What it does:</strong></p>
            <ul className="list-disc pl-4 space-y-1">
              <li>Deletes ALL source files from the knowledge base</li>
              <li>Completely clears the vector database</li>
              <li>Removes all embeddings and metadata</li>
              <li>Starts with a completely clean slate</li>
            </ul>
            <p><strong>When to use:</strong></p>
            <ul className="list-disc pl-4 space-y-1">
              <li>When you want to remove all documents and start fresh</li>
              <li>When you want to completely reset the system</li>
              <li>Before sharing the application with others</li>
            </ul>
            <p className="text-red-700 dark:text-red-300 font-medium">⚠️ DESTRUCTIVE operation - permanently deletes all uploaded files</p>
            <p className="text-red-600 dark:text-red-400 text-xs">A confirmation dialog will appear before proceeding</p>
          </div>
        </div>

        <div className="bg-blue-50 dark:bg-blue-950/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
          <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">🔄 Clear Memory</h4>
          <div className="space-y-2 text-sm">
            <p><strong>What it does:</strong></p>
            <ul className="list-disc pl-4 space-y-1">
              <li>Clears conversation history only</li>
              <li>Keeps all documents and embeddings intact</li>
              <li>Starts a new chat session</li>
            </ul>
            <p><strong>When to use:</strong></p>
            <ul className="list-disc pl-4 space-y-1">
              <li>To start a new conversation</li>
              <li>When you want to ask questions without previous context</li>
              <li>To reset the chat interface</li>
            </ul>
            <p className="text-blue-700 dark:text-blue-300 font-medium">✅ Safe operation - keeps all your documents</p>
          </div>
        </div>

        <div className="bg-amber-50 dark:bg-amber-950/20 p-4 rounded-lg border border-amber-200 dark:border-amber-800">
          <h4 className="font-semibold text-amber-900 dark:text-amber-100 mb-2">📊 Quick Comparison</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Operation</th>
                  <th className="text-left p-2">Source Files</th>
                  <th className="text-left p-2">Vector Database</th>
                  <th className="text-left p-2">Safety</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="p-2 font-medium">Refresh Database</td>
                  <td className="p-2">✅ Keeps</td>
                  <td className="p-2">🔄 Rebuilds</td>
                  <td className="p-2 text-green-600">Safe</td>
                </tr>
                <tr className="border-b">
                  <td className="p-2 font-medium">Clear Database</td>
                  <td className="p-2">🗑️ Deletes</td>
                  <td className="p-2">🗑️ Deletes</td>
                  <td className="p-2 text-red-600">Destructive ⚠️</td>
                </tr>
                <tr>
                  <td className="p-2 font-medium">Clear Memory</td>
                  <td className="p-2">✅ Keeps</td>
                  <td className="p-2">✅ Keeps</td>
                  <td className="p-2 text-green-600">Safe</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    )
  },
  {
    title: "💬 Chat Interface",
    content: (
      <div className="space-y-4">
        <div className="bg-indigo-50 dark:bg-indigo-950/20 p-4 rounded-lg border border-indigo-200 dark:border-indigo-800">
          <h4 className="font-semibold text-indigo-900 dark:text-indigo-100 mb-2">Chat Features</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-indigo-500 rounded-full"></span>
                <strong>Real-time Streaming:</strong> See responses as they're generated
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-indigo-500 rounded-full"></span>
                <strong>Source Citations:</strong> Clickable links to source documents
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-indigo-500 rounded-full"></span>
                <strong>Conversation Memory:</strong> Context-aware follow-up questions
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-indigo-500 rounded-full"></span>
                <strong>Copy Messages:</strong> One-click message copying
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-indigo-500 rounded-full"></span>
                <strong>New Chat:</strong> Start fresh conversations
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-indigo-500 rounded-full"></span>
                <strong>Dark/Light Mode:</strong> Toggle theme preference
              </div>
            </div>
          </div>
        </div>

        <div className="bg-teal-50 dark:bg-teal-950/20 p-4 rounded-lg border border-teal-200 dark:border-teal-800">
          <h4 className="font-semibold text-teal-900 dark:text-teal-100 mb-2">Keyboard Shortcuts</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
            <div>
              <p><kbd className="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded text-xs">Enter</kbd> Send message</p>
              <p><kbd className="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded text-xs">Shift + Enter</kbd> New line</p>
            </div>
            <div>
              <p><kbd className="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded text-xs">Ctrl/Cmd + K</kbd> Focus input</p>
              <p><kbd className="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded text-xs">Escape</kbd> Clear input</p>
            </div>
          </div>
        </div>

        <div className="bg-orange-50 dark:bg-orange-950/20 p-4 rounded-lg border border-orange-200 dark:border-orange-800">
          <h4 className="font-semibold text-orange-900 dark:text-orange-100 mb-2">Question Tips</h4>
          <ul className="list-disc pl-4 space-y-1 text-sm">
            <li>Be specific and detailed in your questions</li>
            <li>Ask follow-up questions for deeper exploration</li>
            <li>Reference specific documents or topics</li>
            <li>Use natural language - no special syntax required</li>
            <li>Ask for summaries, comparisons, or detailed explanations</li>
          </ul>
        </div>
      </div>
    )
  },
  {
    title: "⚙️ Configuration",
    content: (
      <div className="space-y-4">
        <div className="bg-gray-50 dark:bg-gray-950/20 p-4 rounded-lg border border-gray-200 dark:border-gray-800">
          <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">AI Model Settings</h4>
          <div className="space-y-3 text-sm">
            <div>
              <p><strong>Ollama Base URL:</strong> Your local Ollama server address</p>
              <p className="text-gray-600 dark:text-gray-400">Default: http://localhost:11434</p>
            </div>
            <div>
              <p><strong>Embedding Model:</strong> Model for understanding document content</p>
              <p className="text-gray-600 dark:text-gray-400">Default: nomic-embed-text</p>
            </div>
            <div>
              <p><strong>LLM Model:</strong> Model for generating responses</p>
              <p className="text-gray-600 dark:text-gray-400">Default: granite3.1-dense:8b</p>
            </div>
          </div>
        </div>

        <div className="bg-blue-50 dark:bg-blue-950/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
          <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">Document Processing</h4>
          <div className="space-y-3 text-sm">
            <div>
              <p><strong>Chunk Size:</strong> Number of tokens per document chunk</p>
              <p className="text-gray-600 dark:text-gray-400">Default: 1000 (larger for narrative text)</p>
            </div>
            <div>
              <p><strong>Chunk Overlap:</strong> Overlap between chunks for context</p>
              <p className="text-gray-600 dark:text-gray-400">Default: 100 (maintains context)</p>
            </div>
            <div>
              <p><strong>Top K Chunks:</strong> Number of relevant chunks to retrieve</p>
              <p className="text-gray-600 dark:text-gray-400">Default: 5 (more for complex questions)</p>
            </div>
          </div>
        </div>

        <div className="bg-yellow-50 dark:bg-yellow-950/20 p-4 rounded-lg border border-yellow-200 dark:border-yellow-800">
          <h4 className="font-semibold text-yellow-900 dark:text-yellow-100 mb-2">⚠️ Important Configuration Notes</h4>
          <ul className="list-disc pl-4 space-y-1 text-sm">
            <li>Changing embedding model requires database refresh</li>
            <li>Adjusting chunk settings requires database refresh</li>
            <li>Ensure Ollama is running before changing settings</li>
            <li>Larger models provide better quality but use more resources</li>
            <li>Test settings with your specific document types</li>
          </ul>
        </div>
      </div>
    )
  },
  {
    title: "🔧 Troubleshooting",
    content: (
      <div className="space-y-4">
        <div className="bg-red-50 dark:bg-red-950/20 p-4 rounded-lg border border-red-200 dark:border-red-800">
          <h4 className="font-semibold text-red-900 dark:text-red-100 mb-2">Common Issues</h4>
          <div className="space-y-3 text-sm">
            <div>
              <p><strong>❌ &quot;Failed to connect to Ollama&quot;</strong></p>
              <p className="text-gray-600 dark:text-gray-400">Solution: Ensure Ollama is running with <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">ollama serve</code></p>
            </div>
            <div>
              <p><strong>❌ &quot;No relevant documents found&quot;</strong></p>
              <p className="text-gray-600 dark:text-gray-400">Solution: Upload documents and refresh database</p>
            </div>
            <div>
              <p><strong>❌ &quot;Upload failed&quot;</strong></p>
              <p className="text-gray-600 dark:text-gray-400">Solution: Check file format and size, ensure backend is running</p>
            </div>
            <div>
              <p><strong>❌ &quot;Slow responses&quot;</strong></p>
              <p className="text-gray-600 dark:text-gray-400">Solution: Use smaller models or reduce chunk size</p>
            </div>
          </div>
        </div>

        <div className="bg-green-50 dark:bg-green-950/20 p-4 rounded-lg border border-green-200 dark:border-green-800">
          <h4 className="font-semibold text-green-900 dark:text-green-100 mb-2">Performance Optimization</h4>
          <ul className="list-disc pl-4 space-y-1 text-sm">
            <li>Use SSD storage for faster document processing</li>
            <li>Close unnecessary applications to free up RAM</li>
            <li>Use smaller models for faster responses</li>
            <li>Optimize chunk size for your document types</li>
            <li>Consider using GPU acceleration if available</li>
          </ul>
        </div>

        <div className="bg-purple-50 dark:bg-purple-950/20 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
          <h4 className="font-semibold text-purple-900 dark:text-purple-100 mb-2">Getting Help</h4>
          <div className="space-y-2 text-sm">
            <p><strong>📧 Email Support:</strong> <a href="mailto:bolomope2008@gmail.com" className="text-blue-600 hover:underline">bolomope2008@gmail.com</a></p>
            <p><strong>📚 Documentation:</strong> Check the backend and frontend README files</p>
            <p><strong>🐛 Bug Reports:</strong> Include error messages and steps to reproduce</p>
            <p><strong>💡 Feature Requests:</strong> Describe your use case and requirements</p>
          </div>
        </div>
      </div>
    )
  },
  {
    title: "💡 Tips & Best Practices",
    content: (
      <div className="space-y-4">
        <div className="bg-emerald-50 dark:bg-emerald-950/20 p-4 rounded-lg border border-emerald-200 dark:border-emerald-800">
          <h4 className="font-semibold text-emerald-900 dark:text-emerald-100 mb-2">Document Organization</h4>
          <ul className="list-disc pl-4 space-y-1 text-sm">
            <li>Upload related documents together for better context</li>
            <li>Use descriptive filenames for easier source identification</li>
            <li>Organize documents by topic or project</li>
            <li>Consider document quality - better input = better answers</li>
            <li>Regularly update your knowledge base with new documents</li>
          </ul>
        </div>

        <div className="bg-cyan-50 dark:bg-cyan-950/20 p-4 rounded-lg border border-cyan-200 dark:border-cyan-800">
          <h4 className="font-semibold text-cyan-900 dark:text-cyan-100 mb-2">Question Strategies</h4>
          <ul className="list-disc pl-4 space-y-1 text-sm">
            <li>Be specific and detailed in your questions</li>
            <li>Ask follow-up questions to explore topics deeper</li>
            <li>Use comparative questions: &quot;What&apos;s the difference between X and Y?&quot;</li>
            <li>Request summaries: &quot;Summarize the key points about...&quot;</li>
            <li>Ask for examples: &quot;Give me examples of...&quot;</li>
            <li>Always verify critical information against source documents</li>
          </ul>
        </div>

        <div className="bg-pink-50 dark:bg-pink-950/20 p-4 rounded-lg border border-pink-200 dark:border-pink-800">
          <h4 className="font-semibold text-pink-900 dark:text-pink-100 mb-2">Advanced Usage</h4>
          <ul className="list-disc pl-4 space-y-1 text-sm">
            <li>Adjust chunk settings based on document types:
              <ul className="list-disc pl-4 mt-1">
                <li>Larger chunks (1000+) for narrative text and books</li>
                <li>Smaller chunks (500-) for structured data and reports</li>
                <li>Medium chunks (750) for general documents</li>
              </ul>
            </li>
            <li>Use conversation memory for complex multi-step questions</li>
            <li>Experiment with different models for your specific use case</li>
            <li>Monitor system resources during heavy usage</li>
            <li>Backup your knowledge base regularly</li>
          </ul>
        </div>

        <div className="bg-amber-50 dark:bg-amber-950/20 p-4 rounded-lg border border-amber-200 dark:border-amber-800">
          <h4 className="font-semibold text-amber-900 dark:text-amber-100 mb-2">Quality Assurance</h4>
          <ul className="list-disc pl-4 space-y-1 text-sm">
            <li>Always verify important information against source documents</li>
            <li>Cross-reference answers across multiple documents</li>
            <li>Use the source citations to check accuracy</li>
            <li>Report any inaccuracies or hallucinations</li>
            <li>Keep your documents updated and accurate</li>
            <li>Consider the AI as an assistant, not a replacement for human judgment</li>
          </ul>
        </div>
      </div>
    )
  }
] 