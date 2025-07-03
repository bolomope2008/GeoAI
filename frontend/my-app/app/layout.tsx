import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import type React from "react"

export const metadata = {
  title: "GeoAI",
  description: "Intelligent Document Assistant",
  icons: {
    icon: '/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning className="font-sans">
      <head />
      <body className="min-h-screen bg-background text-foreground antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <div className="min-h-screen w-full">
            {children}
          </div>
        </ThemeProvider>
      </body>
    </html>
  )
}

