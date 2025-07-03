import { useState, useRef, useEffect } from "react"
import { Upload, Search, File, RefreshCw, Trash2, X, CheckCircle, AlertCircle } from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { api } from '@/lib/api'
import { useToast } from "@/components/ui/use-toast"
import { useBaseUrl } from '@/app/hooks/useBaseUrl'
import type { FileInfo } from '@/lib/api'
import type { Message } from '@/lib/types'

interface SidebarProps {
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>
}

interface UploadFile {
  file: File
  status: 'pending' | 'uploading' | 'success' | 'error'
  progress: number
  error?: string
}

export function Sidebar({ setMessages }: SidebarProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState<FileInfo[]>([])
  const [isUploadOpen, setIsUploadOpen] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [isClearing, setIsClearing] = useState(false)
  const { baseUrl } = useBaseUrl()
  const [selectedFiles, setSelectedFiles] = useState<UploadFile[]>([])
  const [showResults, setShowResults] = useState(false)
  const searchRef = useRef<HTMLDivElement>(null)
  const { toast } = useToast()

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowResults(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSearch = async (query: string) => {
    setSearchQuery(query)
    try {
      const files = await api.searchFiles(query)
      setSearchResults(files)
      setShowResults(true)
    } catch (error) {
      console.error('Search error:', error)
      setSearchResults([])
      setShowResults(false)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files) {
      const newFiles: UploadFile[] = []
      for (let i = 0; i < files.length; i++) {
        newFiles.push({
          file: files[i],
          status: 'pending',
          progress: 0
        })
      }
      setSelectedFiles(newFiles)
    }
  }

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleFileUpload = async () => {
    if (selectedFiles.length === 0) return

    try {
      setIsUploading(true)
      
      // Update all files to uploading status
      setSelectedFiles(prev => prev.map(file => ({ ...file, status: 'uploading' as const })))
      
      let successCount = 0
      let errorCount = 0
      
      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i]
        
        try {
          // Update progress for this file
          setSelectedFiles(prev => prev.map((f, index) => 
            index === i ? { ...f, progress: 25 } : f
          ))
          
          const result = await api.uploadFile(file.file)
          
          // Update to success
          setSelectedFiles(prev => prev.map((f, index) => 
            index === i ? { 
              ...f, 
              status: 'success' as const, 
              progress: 100 
            } : f
          ))
          
          successCount++
          
          // Log processing details
          if (result.details) {
            console.log(`Processed ${file.file.name}:`, result.details)
          }
          
          // Update progress for next file
          if (i < selectedFiles.length - 1) {
            setSelectedFiles(prev => prev.map((f, index) => 
              index > i ? { ...f, progress: 0 } : f
            ))
          }
          
        } catch (error) {
          // Update to error and show error message
          const errorMsg = error instanceof Error ? error.message : 'Upload failed'
          setSelectedFiles(prev => prev.map((f, index) => 
            index === i ? { 
              ...f, 
              status: 'error' as const, 
              error: errorMsg
            } : f
          ))
          errorCount++
          console.error(`Upload error for ${file.file.name}:`, errorMsg)
        }
      }
      
      // Show appropriate toast message and handle dialog closure
      if (successCount > 0 && errorCount === 0) {
        // All files uploaded successfully
        toast({
          title: "Upload Successful",
          description: `${successCount} file${successCount > 1 ? 's' : ''} uploaded successfully`,
        })
        setSelectedFiles([]) // Clear file selection
        setIsUploadOpen(false) // Close the dialog
      } else if (successCount > 0 && errorCount > 0) {
        // Some files succeeded, some failed
        toast({
          title: "Partial Success",
          description: `${successCount} file${successCount > 1 ? 's' : ''} uploaded, ${errorCount} failed`,
          variant: "default",
        })
        // Keep failed files in the list for user to see errors
        setSelectedFiles(prev => prev.filter(f => f.status === 'error'))
        // Keep dialog open to show errors
      } else {
        // All files failed
        toast({
          title: "Upload Failed",
          description: "All files failed to upload",
          variant: "destructive",
        })
        // Keep failed files in the list for user to see errors
        setSelectedFiles(prev => prev.filter(f => f.status === 'error'))
        // Keep dialog open to show errors
      }
      
      // Refresh the file list
      handleSearch(searchQuery)
      
    } catch (error) {
      console.error('Upload error:', error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : 'Failed to upload files',
        variant: "destructive",
      })
    } finally {
      setIsUploading(false)
    }
  }

  const handleRefreshDatabase = async () => {
    try {
      setIsRefreshing(true)
      await api.refreshDatabase()
      
      // Refresh the file list
      handleSearch(searchQuery)
      
      toast({
        title: "Success",
        description: "Database refreshed successfully",
      })
    } catch (error) {
      console.error('Refresh error:', error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : 'Failed to refresh database',
        variant: "destructive",
      })
    } finally {
      setIsRefreshing(false)
    }
  }

  const handleClearDatabase = async () => {
    try {
      setIsClearing(true)
      await api.clearDatabase()
      
      // Clear the file list since source files are also deleted
      setSearchResults([])
      setSearchQuery("")
      
      toast({
        title: "Success",
        description: "Database and source documents cleared successfully. All files have been removed.",
      })
    } catch (error) {
      console.error('Clear error:', error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : 'Failed to clear database',
        variant: "destructive",
      })
    } finally {
      setIsClearing(false)
    }
  }

  const handleStartNewChat = async () => {
    try {
      await api.clearMemory()
      setMessages([{ role: "assistant", content: "Hello there! How can I help you today?" }])
    } catch (error) {
      console.error('Failed to clear memory:', error)
      toast({
        title: "Error",
        description: "Failed to start new chat",
        variant: "destructive",
      })
    }
  }

  // Format file size to human readable format
  const formatFileSize = (bytes: number): string => {
    const units = ['B', 'KB', 'MB', 'GB']
    let size = bytes
    let unitIndex = 0
    
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024
      unitIndex++
    }
    
    return `${size.toFixed(1)} ${units[unitIndex]}`
  }

  return (
    <div className="w-[260px] h-screen bg-background border-r border-border flex flex-col">
      <ScrollArea className="flex-1 px-2">
        <div className="space-y-4 py-4">
          <div className="space-y-1">
            <div className="relative" ref={searchRef}>
              <Input
                type="text"
                placeholder="Search for file"
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                className="w-full pl-8 text-sm"
                onFocus={() => setShowResults(true)}
              />
              <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              {showResults && searchResults.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-background border border-border rounded-md shadow-lg">
                  {searchResults.map((file, index) => (
                    <a 
                      key={index}
                      href={`${baseUrl}/files/${encodeURIComponent(file.name)}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block p-2 hover:bg-accent border-b border-border last:border-0 cursor-pointer"
                      onClick={() => setShowResults(false)}
                    >
                      <div className="flex items-center gap-2">
                        <File className="h-4 w-4 text-muted-foreground" />
                        <div className="flex-1 min-w-0">
                          <div className="text-sm truncate text-foreground">{file.name}</div>
                          <div className="text-xs text-muted-foreground">
                            {file.type} • {formatFileSize(file.size)}
                          </div>
                        </div>
                      </div>
                    </a>
                  ))}
                </div>
              )}
            </div>
            <Dialog open={isUploadOpen} onOpenChange={setIsUploadOpen}>
              <DialogTrigger asChild>
                <Button 
                  variant="ghost" 
                  className="w-full justify-start gap-2 text-sm text-foreground"
                  disabled={isUploading}
                >
                  <Upload className="h-4 w-4" />
                  {isUploading ? "Uploading..." : "Upload Files"}
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl w-full">
                <DialogHeader>
                  <DialogTitle>Upload Files</DialogTitle>
                  <DialogDescription>
                    Select and upload files to the knowledge base. Supported formats: PDF, DOCX, XLSX, CSV, TXT
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div className="grid w-full max-w-full items-center gap-1.5">
                    <Label htmlFor="files">Select Files</Label>
                    <Input 
                      id="files" 
                      type="file" 
                      onChange={handleFileSelect}
                      disabled={isUploading}
                      accept=".pdf,.docx,.xlsx,.csv,.txt"
                      multiple
                    />
                  </div>
                  
                  {selectedFiles.length > 0 && (
                    <div className="space-y-2">
                      <Label>Selected Files ({selectedFiles.length})</Label>
                      <div className="max-h-40 overflow-y-auto space-y-2 w-full max-w-full">
                        {selectedFiles.map((file, index) => (
                          <div key={index} className="flex items-center gap-2 p-2 border rounded-md w-full max-w-full overflow-hidden">
                            <File className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                            <div className="flex-1 min-w-0 max-w-full">
                              <div className="text-sm truncate max-w-full">{file.file.name}</div>
                              <div className="text-xs text-muted-foreground flex items-center gap-2">
                                {formatFileSize(file.file.size)}
                                {file.status === 'error' && file.error && (
                                  <span
                                    className="text-red-500 ml-2 truncate max-w-[200px] md:max-w-[400px] overflow-hidden inline-block align-bottom"
                                    title={file.error}
                                  >
                                    {file.error}
                                  </span>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center gap-1 flex-shrink-0">
                              {file.status === 'pending' && (
                                <div className="w-4 h-4 border-2 border-gray-300 rounded-full"></div>
                              )}
                              {file.status === 'uploading' && (
                                <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                              )}
                              {file.status === 'success' && (
                                <CheckCircle className="h-4 w-4 text-green-500" />
                              )}
                              {file.status === 'error' && (
                                <AlertCircle className="h-4 w-4 text-red-500" />
                              )}
                              {!isUploading && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => removeFile(index)}
                                  className="h-6 w-6 p-0"
                                >
                                  <X className="h-3 w-3" />
                                </Button>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="flex gap-2">
                    <Button
                      onClick={handleFileUpload}
                      disabled={selectedFiles.length === 0 || isUploading}
                      className="flex-1"
                    >
                      {isUploading ? "Uploading..." : "Upload Files"}
                    </Button>
                    {!isUploading && (
                      <Button
                        variant="outline"
                        onClick={() => {
                          setSelectedFiles([])
                          setIsUploadOpen(false)
                        }}
                      >
                        Cancel
                      </Button>
                    )}
                  </div>
                </div>
              </DialogContent>
            </Dialog>
            <Button 
              variant="ghost" 
              className="w-full justify-start gap-2 text-sm text-foreground"
              onClick={handleRefreshDatabase}
              disabled={isRefreshing}
            >
              <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              {isRefreshing ? "Refreshing..." : "Refresh Database"}
            </Button>
            <Button 
              variant="ghost" 
              className="w-full justify-start gap-2 text-sm text-foreground text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950"
              onClick={() => {
                if (window.confirm("⚠️ WARNING: This will permanently delete ALL uploaded files and clear the database. This action cannot be undone. Are you sure you want to continue?")) {
                  handleClearDatabase()
                }
              }}
              disabled={isClearing}
            >
              <Trash2 className={`h-4 w-4 ${isClearing ? 'animate-spin' : ''}`} />
              {isClearing ? "Clearing..." : "Clear Database"}
            </Button>
          </div>
        </div>
      </ScrollArea>
      <div className="p-4 border-t border-border">
        <Button onClick={handleStartNewChat} variant="outline" className="w-full">
          Start New Chat
        </Button>
      </div>
    </div>
  )
}