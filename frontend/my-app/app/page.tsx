"use client"

import { useState } from "react"
import { Sidebar } from "./components/Sidebar"
import { ChatInterface } from "./components/ChatInterface"
import type { Message } from "@/lib/types"

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Hello there! How can I help you today?" }
  ])

  return (
    <div className="flex h-screen w-full">
      <Sidebar setMessages={setMessages} />
      <main className="flex-1 flex flex-col">
        <ChatInterface messages={messages} setMessages={setMessages} />
      </main>
    </div>
  )
}

