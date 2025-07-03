import type { Source } from './api'

export interface Message {
  role: "assistant" | "user"
  content: string
  sources?: Source[]
  isThinking?: boolean
} 