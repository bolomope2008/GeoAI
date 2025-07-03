# Chatbot Frontend Documentation

A modern, responsive React-based frontend for the Chatbot API, built with Next.js 14, TypeScript, and Tailwind CSS. This application provides an intuitive chat interface for interacting with the RAG-powered chatbot system.

## 🏗️ Architecture Overview

The frontend is built using modern web technologies:

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript development
- **Tailwind CSS**: Utility-first CSS framework
- **Radix UI**: Accessible component primitives
- **Lucide React**: Beautiful icon library
- **React Type Animation**: Typing animation effects

## 📁 Project Structure

```
frontend/my-app/
├── app/                    # Next.js App Router
│   ├── components/         # Reusable UI components
│   │   ├── ChatInterface.tsx    # Main chat component
│   │   ├── ChatMessage.tsx      # Individual message component
│   │   └── Sidebar.tsx          # Navigation sidebar
│   ├── fonts/             # Custom font files
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout component
│   └── page.tsx           # Home page component
├── components/            # Shared UI components
│   ├── ui/               # Base UI components
│   │   ├── avatar.tsx
│   │   ├── button.tsx
│   │   ├── dialog.tsx
│   │   ├── input.tsx
│   │   ├── label.tsx
│   │   ├── scroll-area.tsx
│   │   └── toast.tsx
│   ├── theme-provider.tsx # Theme context provider
│   └── theme-toggle.tsx   # Dark/light mode toggle
├── lib/                   # Utility libraries
│   ├── api.ts            # API client functions
│   ├── help-content.tsx  # Help documentation
│   ├── types.ts          # TypeScript type definitions
│   └── utils.ts          # Utility functions
├── public/               # Static assets
├── Dockerfile           # Container configuration
├── package.json         # Dependencies and scripts
├── tailwind.config.ts   # Tailwind CSS configuration
└── tsconfig.json        # TypeScript configuration
```

## 🚀 Quick Start

### Prerequisites

1. **Node.js 18+**
2. **npm** or **yarn**
3. **Backend API** running (see backend documentation)

### Installation

```bash
# Navigate to frontend directory
cd frontend/my-app

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:3001`

### Docker Deployment

```bash
# Build the image
docker build -t chatbot-frontend .

# Run the container
docker run -p 3001:3000 chatbot-frontend
```

## 🎨 UI Components

### Core Components

#### `ChatInterface`
The main chat component that handles:
- Message display and input
- Real-time streaming responses
- File upload functionality
- Conversation management

**Features:**
- Real-time message streaming
- File upload with drag-and-drop
- Message history with scroll restoration
- Loading states and error handling

#### `ChatMessage`
Individual message component displaying:
- User and AI messages
- Source citations and metadata
- Message timestamps
- Copy-to-clipboard functionality

#### `Sidebar`
Navigation sidebar containing:
- Theme toggle (dark/light mode)
- Help documentation
- Settings panel
- File management

### UI Component Library

Built with **Radix UI** primitives for accessibility:

- **Button**: Accessible button component with variants
- **Input**: Form input with validation states
- **Dialog**: Modal dialogs for settings and help
- **Toast**: Notification system for user feedback
- **Avatar**: User avatar display
- **ScrollArea**: Custom scrollable areas

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file in the frontend directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Feature Flags
NEXT_PUBLIC_ENABLE_STREAMING=true
NEXT_PUBLIC_ENABLE_FILE_UPLOAD=true

# Analytics (optional)
NEXT_PUBLIC_ANALYTICS_ID=your-analytics-id
```

### Tailwind CSS Configuration

Custom configuration in `tailwind.config.ts`:

```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        // ... more color definitions
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}

export default config
```

## 📡 API Integration

### API Client (`lib/api.ts`)

Centralized API communication functions:

```typescript
// Chat API
export async function sendMessage(message: string): Promise<ChatResponse>
export async function sendMessageStream(message: string): Promise<ReadableStream>

// File Management
export async function uploadFile(file: File): Promise<UploadResponse>
export async function searchFiles(query: string): Promise<FileInfo[]>

// System Management
export async function getSettings(): Promise<Settings>
export async function updateSettings(settings: Settings): Promise<void>
export async function clearMemory(): Promise<void>
```

### Real-time Streaming

The frontend supports real-time message streaming:

```typescript
// Stream chat response
const stream = await sendMessageStream(message);
const reader = stream.getReader();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  // Process streaming data
  const chunk = new TextDecoder().decode(value);
  // Update UI with streaming content
}
```

## 🎯 Key Features

### Chat Interface
- **Real-time Streaming**: Live token-by-token response display
- **Message History**: Persistent conversation memory
- **Source Citations**: Clickable source references
- **File Upload**: Drag-and-drop document upload
- **Copy Messages**: One-click message copying

### User Experience
- **Dark/Light Mode**: Theme switching with system preference detection
- **Responsive Design**: Mobile-first responsive layout
- **Accessibility**: WCAG 2.1 AA compliant components
- **Loading States**: Smooth loading animations
- **Error Handling**: User-friendly error messages

### File Management
- **Document Upload**: Support for PDF, DOCX, XLSX, CSV, TXT
- **File Search**: Search through uploaded documents
- **File Preview**: View uploaded files
- **Upload Progress**: Real-time upload progress indicators

## 🎨 Styling and Theming

### Design System

Built with a consistent design system:

- **Color Palette**: Semantic color tokens
- **Typography**: Custom font stack with Geist fonts
- **Spacing**: Consistent spacing scale
- **Components**: Reusable component patterns

### Theme Support

```typescript
// Theme context provider
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')
  
  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}
```

### CSS Variables

Dynamic theming with CSS custom properties:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;
  /* ... more variables */
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --primary: 210 40% 98%;
  --primary-foreground: 222.2 47.4% 11.2%;
  /* ... dark theme variables */
}
```

## 🔧 Development

### Development Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint

# Type checking
npx tsc --noEmit
```

### Code Quality

- **ESLint**: Code linting with Next.js configuration
- **TypeScript**: Strict type checking
- **Prettier**: Code formatting (if configured)
- **Husky**: Git hooks for pre-commit checks

### Testing

```bash
# Run tests (if configured)
npm test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

## 🚀 Performance Optimization

### Next.js Optimizations

- **App Router**: Latest Next.js routing system
- **Server Components**: Reduced client-side JavaScript
- **Image Optimization**: Automatic image optimization
- **Font Optimization**: Custom font loading
- **Code Splitting**: Automatic code splitting

### Bundle Optimization

- **Tree Shaking**: Unused code elimination
- **Dynamic Imports**: Lazy loading of components
- **Bundle Analysis**: Webpack bundle analyzer
- **Compression**: Gzip/Brotli compression

### Caching Strategies

- **Static Generation**: Pre-rendered pages
- **Incremental Static Regeneration**: Dynamic content updates
- **Service Worker**: Offline functionality
- **Browser Caching**: Optimized cache headers

## 🐳 Docker Deployment

### Multi-stage Build

```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
ENV PORT 3000
ENV NODE_ENV production

CMD ["node", "server.js"]
```

### Docker Compose

```yaml
services:
  frontend:
    build: ./frontend/my-app
    ports:
      - "3001:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
```

## 🔍 Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check `NEXT_PUBLIC_API_URL` environment variable
   - Verify backend server is running
   - Check CORS configuration

2. **Build Errors**
   - Clear `.next` directory: `rm -rf .next`
   - Reinstall dependencies: `rm -rf node_modules && npm install`
   - Check TypeScript errors: `npx tsc --noEmit`

3. **Styling Issues**
   - Verify Tailwind CSS configuration
   - Check CSS import order
   - Clear browser cache

4. **Performance Issues**
   - Analyze bundle size: `npm run analyze`
   - Check for memory leaks
   - Optimize images and assets

### Debug Mode

```bash
# Enable debug logging
DEBUG=* npm run dev

# Check build output
npm run build --verbose
```

## 📱 Responsive Design

### Breakpoints

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Mobile Optimizations

- Touch-friendly interface
- Optimized keyboard handling
- Reduced bundle size
- Progressive Web App features

## 🔒 Security

### Security Headers

```typescript
// next.config.js
const nextConfig = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ]
  },
}
```

### Input Validation

- Client-side validation with TypeScript
- Server-side validation for API calls
- XSS protection with React
- CSRF protection with Next.js

## 📊 Analytics and Monitoring

### Performance Monitoring

- **Core Web Vitals**: LCP, FID, CLS tracking
- **Bundle Analysis**: Webpack bundle analyzer
- **Error Tracking**: Error boundary implementation
- **User Analytics**: Optional analytics integration

### Error Boundaries

```typescript
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback />;
    }
    return this.props.children;
  }
}
```

## 🤝 Contributing

### Development Guidelines

1. **Code Style**: Follow ESLint and Prettier configuration
2. **TypeScript**: Use strict typing for all components
3. **Testing**: Write unit tests for new features
4. **Documentation**: Update documentation for API changes
5. **Accessibility**: Ensure WCAG 2.1 AA compliance

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create pull request
git push origin feature/new-feature
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

For more information about the backend API, see the [Backend Documentation](../backend/README.md). 