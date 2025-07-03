import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ChatMessage } from "./ChatMessage"
import { Send, Settings, HelpCircle, Square } from "lucide-react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import { api, getBaseUrl } from '@/lib/api'
import { useToast } from "@/components/ui/use-toast"
import type { Source, Config } from '@/lib/api'
import { helpSections } from "@/lib/help-content"
import { ThemeToggle } from "@/components/theme-toggle"

interface ChatInterfaceProps {
  messages: Message[]
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>
}

interface Message {
  role: "assistant" | "user"
  content: string
  sources?: Source[]
  isThinking?: boolean
}

export function ChatInterface({ messages, setMessages }: ChatInterfaceProps) {
  const [isThinking, setIsThinking] = useState(false)
  const [isConfigOpen, setIsConfigOpen] = useState(false)
  const [config, setConfig] = useState<Config>({
    ollama_base_url: `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:11434`,
    embedding_model: "nomic-embed-text",
    llm_model: "phi4:14b-fp16",
    chunk_size: 1000,
    chunk_overlap: 100,
    top_k_chunks: 5,
  })
  const [isProcessing, setIsProcessing] = useState(false)
  const [isHelpOpen, setIsHelpOpen] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const { toast } = useToast()

  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Load initial configuration
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const config = await api.getConfig()
        setConfig(config)
      } catch (error) {
        console.error('Failed to load config:', error)
        toast({
          title: "Error",
          description: "Failed to load configuration",
          variant: "destructive",
        })
      }
    }
    loadConfig()
  }, [toast])

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSaveConfig = async (shouldRefresh: boolean = false) => {
    try {
      setIsSaving(true)
      await api.updateConfig(config)
      
      toast({
        title: "Success",
        description: "Configuration saved successfully",
      })

      if (shouldRefresh) {
        await api.refreshDatabase()
        toast({
          title: "Success",
          description: "Database refreshed with new settings",
        })
      }

      setIsConfigOpen(false)
    } catch (error) {
      console.error('Failed to save config:', error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : 'Failed to save configuration',
        variant: "destructive",
      })
    } finally {
      setIsSaving(false)
    }
  }

  const handleConfigChange = (key: keyof Config, value: string) => {
    // Convert numeric strings to numbers for specific fields
    if (key === 'chunk_size' || key === 'chunk_overlap' || key === 'top_k_chunks') {
      const numValue = parseInt(value)
      if (!isNaN(numValue)) {
        setConfig(prev => ({ ...prev, [key]: numValue }))
      }
    } else {
      setConfig(prev => ({ ...prev, [key]: value }))
    }
  }

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    const textarea = textareaRef.current
    if (!textarea) return

    const message = textarea.value.trim()
    if (!message || isProcessing) return

    try {
      setError(null)
      setIsProcessing(true)
      textarea.value = ""
      textarea.style.height = "auto"

      // Add user message immediately
      setMessages(prev => [...prev, { role: "user", content: message }])
      
      // Add assistant message in thinking state
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: "",
        isThinking: true 
      }])

      try {
        const baseUrl = await getBaseUrl();
        const response = await fetch(`${baseUrl}/chat/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message })
        });

        if (!response.ok) {
          throw new Error('Failed to get response');
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body');
        }

        const decoder = new TextDecoder();
        let buffer = '';
        let messageContent = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            const trimmedLine = line.trim();
            if (trimmedLine.startsWith('data: ')) {
              try {
                console.log('Received SSE message:', trimmedLine);
                const data = JSON.parse(trimmedLine.slice(6));
                console.log('Parsed data:', data);
                if (data.type === 'sources') {
                  console.log('Received sources at:', new Date().toISOString());
                  setMessages(prev => {
                    const newMessages = [...prev];
                    const lastMessage = newMessages[newMessages.length - 1];
                    if (lastMessage.role === 'assistant') {
                      lastMessage.sources = data.sources;
                      // Keep thinking until first token
                      lastMessage.isThinking = true;
                    }
                    return newMessages;
                  });
                } else if (data.type === 'token') {
                  if (data.content !== undefined) {
                    console.log('Received token at:', new Date().toISOString(), 'Token:', data.content);
                    messageContent += data.content;
                    setMessages(prev => {
                      const newMessages = [...prev];
                      const lastMessage = newMessages[newMessages.length - 1];
                      if (lastMessage.role === 'assistant') {
                        // Stop thinking as soon as we get first token
                        lastMessage.isThinking = false;
                        lastMessage.content = messageContent;
                      }
                      return newMessages;
                    });
                  }
                } else if (data.type === 'error') {
                  throw new Error(data.error || 'Unknown error occurred');
                } else if (data.type === 'done' || data.done) {
                  console.log('Stream completed');
                  setIsProcessing(false);
                }
              } catch (e) {
                console.error('Failed to parse SSE message:', e);
                throw e;
              }
            }
          }
        }
        setIsProcessing(false); // Ensure processing state is reset after stream ends
      } catch (error) {
        console.error('Chat error:', error);
        setError(error instanceof Error ? error.message : 'Failed to get response');
        setMessages(prev => prev.slice(0, -1));
        setIsProcessing(false);
      }
    } catch (error) {
      console.error('Chat error:', error);
      setError(error instanceof Error ? error.message : 'Failed to get response');
      setMessages(prev => prev.slice(0, -1));
      setIsProcessing(false);
    }
  }

  const handleStop = () => {
    setIsThinking(false)
    setIsProcessing(false)
  }

  const formatLabel = (key: string) => {
    return key
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(" ")
  }

  const adjustTextareaHeight = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const textarea = e.target
    textarea.style.height = "auto"
    textarea.style.height = `${textarea.scrollHeight}px`
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter") {
      if (e.shiftKey) {
        // Shift+Enter: allow new line
        return
      } else {
        // Enter without Shift: send the chat
        e.preventDefault()
        handleSubmit()
      }
    }
  }

  useEffect(() => {
    if (error) {
      toast({
        title: "Error",
        description: error,
        variant: "destructive",
      });
    }
  }, [error, toast]);

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-background [&_.animate-spin-slow]:animate-[spin_5s_linear_infinite]">
      {/* Header */}
      <div className="flex items-center h-14 flex-shrink-0 max-w-5xl mx-auto w-full px-4">
        {/* Left spacer */}
        <div className="w-[100px]"></div>
        
        {/* Center content */}
        <div className="flex-1 flex items-center justify-center">
          <div className="flex items-center">
            <svg
              className="w-6 h-6 mr-2 animate-spin-slow text-foreground dark:text-white"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
              <path
                d="M12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2ZM12 20C7.58172 20 4 16.4183 4 12C4 7.58172 7.58172 4 12 4C16.4183 4 20 7.58172 20 12C20 16.4183 16.4183 20 12 20Z"
                fill="currentColor"
              />
              <path d="M12 2C6.47715 2 2 6.47715 2 12H4C4 7.58172 7.58172 4 12 4V2Z" fill="currentColor" />
            </svg>
            <h1 className="text-xl font-semibold text-foreground dark:text-white">GeoAI</h1>
          </div>
        </div>
        
        {/* Right actions */}
        <div className="w-[100px] flex items-center justify-end gap-2">
          <ThemeToggle />
          <Dialog open={isConfigOpen} onOpenChange={setIsConfigOpen}>
            <DialogTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <Settings className="h-4 w-4" />
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader className="text-center">
                <DialogTitle className="text-xl font-semibold">Configuration</DialogTitle>
                <DialogDescription>
                  Configure GeoAI settings including Ollama connection, models, and document processing parameters
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                {Object.entries(config).map(([key, value]) => (
                  <div key={key} className="grid grid-cols-3 items-center gap-4">
                    <Label htmlFor={key} className="text-right whitespace-normal break-words">
                      {formatLabel(key)}
                    </Label>
                    <Input
                      id={key}
                      value={value}
                      onChange={(e) => handleConfigChange(key as keyof Config, e.target.value)}
                      className="col-span-2"
                      disabled={isSaving}
                      type={key === 'chunk_size' || key === 'chunk_overlap' || key === 'top_k_chunks' ? 'number' : 'text'}
                      min={key === 'chunk_size' || key === 'chunk_overlap' || key === 'top_k_chunks' ? 1 : undefined}
                    />
                  </div>
                ))}
              </div>
              <p className="text-red-500 text-xs mt-2">
                Updating the embedding model and chunk information will require a database refresh.
              </p>
              <div className="flex justify-end space-x-2 mt-4">
                <Button
                  onClick={() => handleSaveConfig(false)}
                  disabled={isSaving}
                >
                  {isSaving ? "Saving..." : "Save"}
                </Button>
                <Button
                  onClick={() => handleSaveConfig(true)}
                  variant="default"
                  disabled={isSaving}
                >
                  {isSaving ? "Saving..." : "Save and Update DB"}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-grow overflow-y-auto max-w-5xl mx-auto w-full px-4">
        <ScrollArea>
          {messages.map((message, index) => (
            <ChatMessage 
              key={index} 
              role={message.role}
              content={message.content}
              isThinking={message.isThinking}
              sources={message.sources}
            />
          ))}
          {error && (
            <div className="p-4 my-2 bg-destructive/10 text-destructive rounded-lg">
              {error}
            </div>
          )}
        </ScrollArea>
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 flex-shrink-0">
        <div className="max-w-5xl mx-auto flex flex-col gap-4">
          <form onSubmit={handleSubmit} className="w-full relative">
            <textarea
              ref={textareaRef}
              name="message"
              placeholder="Message GeoAI..."
              className="w-full bg-muted pr-20 py-6 px-4 rounded-xl border border-input text-sm resize-none"
              onKeyDown={handleKeyDown}
              onChange={adjustTextareaHeight}
              rows={1}
              style={{ minHeight: "60px" }}
              disabled={isProcessing}
            />
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="absolute right-2 top-1/2 -translate-y-1/2"
              onClick={isProcessing ? handleStop : handleSubmit}
              disabled={isThinking && !isProcessing}
            >
              {isProcessing ? <Square className="h-4 w-4" /> : <Send className="h-4 w-4" />}
            </Button>
          </form>
        </div>
        <div className="flex items-center justify-center mt-2 text-xs text-muted-foreground relative max-w-5xl mx-auto">
          <span className="text-center">GeoAI can make mistakes. Consider checking important information.</span>
          <Dialog open={isHelpOpen} onOpenChange={setIsHelpOpen}>
            <DialogTrigger asChild>
              <Button variant="ghost" size="icon" className="h-6 w-6 absolute right-0">
                <HelpCircle className="h-4 w-4" />
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[850px] sm:max-h-[80vh]">
              <DialogHeader>
                <DialogTitle>Help & Documentation</DialogTitle>
                <DialogDescription>
                  Learn how to use GeoAI effectively with comprehensive documentation and examples
                </DialogDescription>
              </DialogHeader>
              <ScrollArea className="mt-4 h-[600px] w-full rounded-md border p-4">
                <div className="space-y-6">
                  {helpSections.map((section, index) => (
                    <div key={index} className="space-y-2">
                      <h3 className="text-lg font-semibold">{section.title}</h3>
                      {section.content}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </DialogContent>
          </Dialog>
        </div>
      </div>
    </div>
  )
}

