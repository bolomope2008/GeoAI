import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Avatar } from "@/components/ui/avatar"
import { Bot, Copy, Check, ExternalLink } from "lucide-react"
import type { Source } from "@/lib/api"
import { useBaseUrl } from "@/app/hooks/useBaseUrl"
import React from "react"

interface ChatMessageProps {
  role: "assistant" | "user"
  content: string
  isThinking?: boolean
  sources?: Source[]
}

export function ChatMessage({ role, content, isThinking, sources }: ChatMessageProps) {
  const [isCopied, setIsCopied] = useState(false)
  const { baseUrl } = useBaseUrl()

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content)
    setIsCopied(true)
    setTimeout(() => setIsCopied(false), 2000)
  }

  const renderContent = () => {
    if (isThinking) {
      return (
        <div className="flex items-center gap-2">
          <div className="animate-pulse">Thinking...</div>
        </div>
      )
    }

    return (
      <div>
        <div className="whitespace-pre-wrap">{content}</div>
        {!isThinking && sources && sources.length > 0 && (
          <div className="mt-2 text-xs">
            <span className="text-muted-foreground">Sources:</span>
            <div className="mt-1 flex flex-wrap gap-2">
              {sources.map((s, i) => (
                <a 
                  key={i}
                  href={`${baseUrl}/files/${encodeURIComponent(s.source)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-secondary hover:bg-secondary/80 text-secondary-foreground hover:text-secondary-foreground/90 transition-colors"
                >
                  <ExternalLink className="h-3 w-3" />
                  {s.source}
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  if (role === "user") {
    return (
      <div className="py-4 flex justify-end">
        <div className="max-w-3xl px-4">
          <div className="bg-primary text-primary-foreground dark:bg-zinc-800 dark:text-white px-4 py-2 rounded-3xl">
            <div className="text-sm whitespace-pre-wrap">{content}</div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="py-4">
      <div className="max-w-3xl mx-auto flex gap-4 px-4">
        <Avatar className="h-8 w-8 rounded-sm flex-shrink-0 bg-secondary dark:bg-secondary/80">
          <Bot className="h-6 w-6 text-foreground dark:text-white" />
        </Avatar>

        <div className="flex-1 space-y-1">
          <div className="font-semibold text-sm dark:text-white">GeoAI</div>
          <div className="text-foreground dark:text-gray-200 text-sm">{renderContent()}</div>
          {content && !isThinking && (
            <div className="flex items-center gap-2 mt-1">
              <Button variant="ghost" size="icon" className="h-6 w-6" onClick={handleCopy}>
                {isCopied ? 
                  <Check className="h-3 w-3 text-green-500" /> : 
                  <Copy className="h-3 w-3 dark:text-gray-400" />
                }
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}