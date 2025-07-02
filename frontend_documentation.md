## GeoAI Frontend Documentation

### Overview

The GeoAI frontend is a modern, responsive web application built with Next.js and React, providing an intuitive user interface for the GeoAI RAG chatbot. It allows users to interact with the AI, manage their knowledge base documents, and configure backend settings.

### Technologies Used

*   **Next.js**: React framework for building full-stack web applications.
*   **React**: JavaScript library for building user interfaces.
*   **Shadcn UI**: A collection of accessible and customizable UI components.
*   **Tailwind CSS**: A utility-first CSS framework for styling.
*   **TypeScript**: For type-safe JavaScript development.

### Setup and Installation

1.  **Navigate to the frontend directory:**
    ```bash
    cd GeoAI_V2/frontend/my-app
    ```
2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```
3.  **Run the development server:**
    ```bash
    npm run dev
    ```
    The frontend application will be accessible at `http://localhost:3001`.

### Project Structure (Frontend Specific)

*   `app/`: Contains the core Next.js application pages and layouts.
    *   `layout.tsx`: Root layout for the application, including `ThemeProvider` for dark/light mode.
    *   `page.tsx`: The main application page, integrating the `Sidebar` and `ChatInterface`.
    *   `globals.css`: Global CSS styles, including Tailwind CSS imports.
    *   `components/`: Reusable React components specific to the application.
        *   `ChatInterface.tsx`: The main chat component, handling message display, input, and configuration.
        *   `ChatMessage.tsx`: Renders individual chat messages and their sources.
        *   `Sidebar.tsx`: Manages file uploads, search, and database operations.
*   `components/`: Shared UI components from Shadcn UI (e.g., `ui/button.tsx`, `ui/dialog.tsx`).
*   `lib/`: Utility functions and API services.
    *   `api.ts`: Defines interfaces and the `ApiService` class for interacting with the backend.
    *   `types.ts`: Defines common TypeScript interfaces for data structures.
    *   `utils.ts`: General utility functions (e.g., `cn` for Tailwind CSS class merging).
    *   `help-content.tsx`: Contains the content for the help dialog.
*   `public/`: Static assets like `favicon.ico`.
*   `next.config.mjs`: Next.js configuration file.
*   `tailwind.config.js`, `postcss.config.mjs`: Tailwind CSS configuration.
*   `package.json`: Project metadata and dependencies.

### Key Components and Functionality

#### 1. `ChatInterface.tsx`

This is the central component for user interaction with the chatbot.

*   **Chat Display**: Renders a list of `ChatMessage` components, showing both user and assistant messages.
*   **Message Input**: A `textarea` for users to type their messages, with dynamic resizing and `Shift+Enter` for newlines.
*   **Streaming Responses**: Connects to the backend's `/chat/stream` endpoint to receive and display AI responses token by token, providing a real-time chat experience.
*   **Source Display**: Shows relevant document sources for AI answers, with links to view the original files.
*   **Configuration Dialog**:
    *   Accessed via the `Settings` icon.
    *   Allows users to view and update backend settings such as `ollama_base_url`, `llm_model`, `embedding_model`, `chunk_size`, `chunk_overlap`, and `top_k_chunks`.
    *   Changes can be saved to the backend's `configuration.py` file.
    *   Option to "Save and Update DB" which triggers a database refresh on the backend after saving settings.
*   **Help Dialog**:
    *   Accessed via the `HelpCircle` icon.
    *   Provides information and documentation about the application's features.
*   **Theming**: Integrates `ThemeToggle` for switching between light and dark modes.

#### 2. `ChatMessage.tsx`

Responsible for rendering individual chat bubbles.

*   **Role-based Styling**: Differentiates between user messages (right-aligned, primary background) and assistant messages (left-aligned, secondary background).
*   **Content Display**: Renders the message text, handling `whitespace-pre-wrap` for proper formatting.
*   **Thinking Indicator**: Displays a "Thinking..." animation for assistant messages while the response is being generated.
*   **Source Citations**: If `sources` are provided, it lists them with links to the original documents.
*   **Copy to Clipboard**: A button to easily copy the assistant's response.

#### 3. `Sidebar.tsx`

Provides document management and utility functions.

*   **File Search**:
    *   An input field to search for files within the knowledge base.
    *   Displays search results with file name, size, and type.
    *   Links to view the actual files served by the backend.
*   **File Upload**:
    *   A dialog for selecting and uploading multiple files.
    *   Supports PDF, DOCX, XLSX, CSV, and TXT formats.
    *   Shows upload progress and status (pending, uploading, success, error) for each file.
    *   Provides error messages for failed uploads.
*   **Refresh Database**: Triggers the backend's `/refresh` endpoint to re-index all documents in the knowledge base. Useful after adding new files directly to the `knowledge_base` directory or changing chunking settings.
*   **Clear Database**: **CAUTION: This action permanently deletes all uploaded files and clears the entire ChromaDB.** A confirmation prompt is displayed before execution.
*   **Start New Chat**: Clears the current conversation memory by calling the backend's `/clear-memory` endpoint, effectively starting a fresh chat session.
*   **File Size Formatting**: Utility to display file sizes in a human-readable format (e.g., KB, MB).

#### 4. `lib/api.ts`

This file defines the `ApiService` class, which centralizes all communication with the GeoAI backend.

*   **`getBaseUrl()`**: Dynamically determines the backend API URL based on the environment (browser or server).
*   **Methods**: Provides asynchronous methods for:
    *   `chat(message: string)`: Sends a chat message (though `chat/stream` is primarily used by `ChatInterface`).
    *   `uploadFile(file: File)`: Uploads a single file.
    *   `searchFiles(query?: string)`: Searches for files.
    *   `refreshDatabase()`: Triggers database refresh.
    *   `clearMemory()`: Clears conversation memory.
    *   `clearDatabase()`: Clears the entire database.
    *   `getConfig()`: Retrieves current backend settings.
    *   `updateConfig(config: Config)`: Updates backend settings.
*   **Error Handling**: Each method includes basic error handling, throwing an `Error` with details from the backend response if the request fails.
*   **Interfaces**: Defines TypeScript interfaces for data structures exchanged with the backend (`Source`, `ChatResponse`, `FileInfo`, `Config`, `StreamResponse`).

### Styling

*   **Tailwind CSS**: Used for all styling, providing a highly customizable and efficient way to build the UI.
*   **Shadcn UI**: Provides pre-built, accessible, and customizable components that integrate seamlessly with Tailwind CSS.
*   **Dark Mode**: The application supports a dark mode, which can be toggled via the `ThemeToggle` component in the header.

### Development Notes

*   **Backend Dependency**: The frontend relies heavily on the GeoAI backend being up and running. Ensure the backend is accessible at `http://localhost:8000` (or the configured `OLLAMA_BASE_URL` in `backend/configuration.py`).
*   **Environment Variables**: The `NEXT_PUBLIC_API_URL` environment variable can be used to specify the backend URL if it's not running on `http://localhost:8000`.
*   **Hot Reloading**: During development (`npm run dev`), changes to React components and other files will automatically trigger a hot reload in the browser.
*   **TypeScript**: The project is written in TypeScript, providing type safety and improved developer experience.
