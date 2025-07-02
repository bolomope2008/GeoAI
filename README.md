# GeoAI Desktop

A privacy-first desktop application that lets you chat with your documents using AI - completely offline. Your data never leaves your machine.

![Platform Support](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-blue)
![Privacy](https://img.shields.io/badge/privacy-100%25%20local-green)
![License](https://img.shields.io/badge/license-MIT-green)

## 🔒 **Complete Privacy & Security**

**Your documents stay on YOUR computer.** GeoAI Desktop processes everything locally using your own AI models - no internet required after setup, no data sharing, no third-party servers.

- ✅ **100% Local Processing** - All AI runs on your machine
- ✅ **No Data Upload** - Documents never leave your computer  
- ✅ **No Internet Required** - Works completely offline
- ✅ **No Telemetry** - Zero tracking or data collection
- ✅ **Secure Storage** - All data encrypted and stored locally

## 🧠 **Intelligent Document Chat**

Transform any document into an interactive AI assistant. Upload your files and start asking questions - the AI understands context and provides accurate answers based solely on your documents.

### **Supported File Types**
- 📄 **PDFs** - Research papers, reports, manuals
- 📝 **Text Files** - Notes, documentation, articles  
- 📊 **Spreadsheets** - CSV, XLSX data files
- 🗎 **Word Documents** - DOCX files and reports

### **Key Features**
- **🎯 Contextual Answers** - AI responds based on your specific documents
- **⚡ Real-time Chat** - Streaming responses with conversation memory
- **🔍 Source Citations** - See exactly which documents inform each answer
- **📚 Multi-Document** - Upload and query across multiple files simultaneously
- **💬 Natural Language** - Ask questions in plain English
- **🧠 Memory** - Maintains conversation context across your session

## 📥 **Download & Install**

### macOS
- **Apple Silicon (M1/M2/M3)**: [Download ARM64 DMG](link-to-arm64-dmg)
- **Intel Macs**: [Download Intel DMG](link-to-intel-dmg)

### Windows  
- **Windows 10/11**: [Download Windows Installer](link-to-windows-exe)

### Installation
1. Download the appropriate installer for your system
2. Install the application (drag to Applications on macOS, run installer on Windows)
3. Install [Ollama](https://ollama.ai) for AI functionality
4. Launch GeoAI Desktop and start uploading your documents!

## 🚀 **How It Works**

1. **📂 Upload Documents** - Drag and drop your files into the app
2. **🤖 Install AI Model** - One-time setup with Ollama (runs locally)
3. **💬 Start Chatting** - Ask questions about your documents
4. **🔒 Stay Private** - Everything processes on your machine

```
Your Documents → Local AI Processing → Intelligent Answers
     ↓               ↓                        ↓
  📄 PDFs         🧠 RAG Engine          💬 Chat Interface
  📝 DOCX         🔍 Vector Search       📊 Source Citations
  📊 CSV          🤖 Local LLM          🔒 100% Private
```

## 🛡️ **Why Choose GeoAI Desktop?**

### **Privacy-First Design**
Unlike cloud-based AI tools, GeoAI Desktop keeps your sensitive documents completely private:

- **No API Keys Required** - No OpenAI, Claude, or other third-party services
- **No Internet Dependencies** - Works offline after initial setup
- **No Data Logging** - We can't see your data because it never leaves your computer
- **Corporate Safe** - Perfect for confidential business documents
- **Research Safe** - Ideal for sensitive academic or personal research

### **Professional Use Cases**
- **Legal Documents** - Analyze contracts and legal papers privately
- **Medical Records** - Query patient files without HIPAA concerns  
- **Financial Reports** - Analyze sensitive financial data securely
- **Research Papers** - Academic research without data exposure
- **Personal Documents** - Tax records, personal files, family documents
- **Business Intelligence** - Analyze company reports and data confidentially

## ⚙️ **Technical Requirements**

### **System Requirements**
- **RAM**: 8GB recommended (4GB minimum)
- **Storage**: 2GB free space
- **Internet**: Only for initial Ollama setup

### **AI Requirements**  
- **[Ollama](https://ollama.ai)** - Free, local AI runtime
- **LLM Model** - Download any model (llama2, codellama, etc.)
- **First-time Setup**: ~10-15 minutes to download AI model

### **Platform Support**
- **macOS**: 10.15+ (Apple Silicon & Intel)
- **Windows**: 10/11 (64-bit)
- **Coming Soon**: Linux support

## 🔧 **Setup Guide**

### **Quick Start (5 minutes)**

1. **Install GeoAI Desktop**
   - Download and install from links above

2. **Install Ollama**
   ```bash
   # macOS
   brew install ollama
   
   # Windows - download from ollama.ai
   ```

3. **Download an AI Model**
   ```bash
   ollama pull llama2
   # or any other model you prefer
   ```

4. **Start Using**
   - Launch GeoAI Desktop
   - Upload your documents
   - Start asking questions!

## 🏢 **Perfect for Organizations**

**Compliance-Ready**: Meets strict data privacy requirements
- **GDPR Compliant** - No data processing outside your control
- **HIPAA Safe** - Medical documents stay on your systems  
- **SOX Compliant** - Financial data never transmitted
- **Enterprise Ready** - Deploy across teams without data exposure

**Cost-Effective**: No per-user API costs or subscription fees
- **One-Time Purchase** - No monthly AI service fees
- **Unlimited Usage** - Process as many documents as needed
- **No User Limits** - Install on multiple machines

## 🤝 **Community & Support**

- **📖 Documentation**: [Complete guides and tutorials](docs/)
- **🐛 Issues**: [Report bugs or request features](../../issues)
- **💬 Discussions**: [Community support and ideas](../../discussions)
- **📧 Contact**: [Direct support](mailto:support@example.com)

## 📄 **License**

MIT License - Free for personal and commercial use. See [LICENSE](LICENSE) for details.

---

## 🔍 **For Developers**

Interested in the technical implementation? Check out our [build documentation](docs/) to see how we created this privacy-first RAG application using:

- **Frontend**: Next.js + TypeScript
- **Backend**: FastAPI + LangChain + ChromaDB  
- **Desktop**: Electron with secure architecture
- **AI**: Local Ollama integration

---

*Your documents. Your AI. Your privacy.* 🔒