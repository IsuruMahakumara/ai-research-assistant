# AI Research Assistant - Frontend Specification

## Overview

Build a React-based chat interface for the AI Research Assistant backend. The application helps users query a knowledge base (currently GDPR documents) and receive AI-generated answers with source citations.

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Framework | React 18+ |
| Language | TypeScript |
| Styling | Tailwind CSS |
| HTTP Client | Fetch API or Axios |
| Build Tool | Vite |

---

## Core Features

### 1. Chat Interface

A conversational UI where users can:
- Type and submit questions
- View AI-generated responses
- See source document citations for each answer

### 2. Source Citations Panel

Display the retrieved documents that informed each answer:
- Article number
- Relevance score (as percentage or visual indicator)
- Expandable text preview

### 3. Loading States

Show clear feedback when:
- Query is being processed
- Response is being generated

---

## API Integration

### Endpoint

```
POST /chat
```

### Request Body

```typescript
interface ChatRequest {
  query: string;      // User's question (required, min 1 char)
  top_k?: number;     // Number of sources to retrieve (1-10, default: 3)
}
```

### Response

```typescript
interface RetrievedDocument {
  id: string;           // Document ID
  article_num: string;  // Article reference (e.g., "Article 5")
  text: string;         // Document content
  score: number;        // Relevance score (0-1)
}

interface ChatResponse {
  query: string;                    // Original query echoed back
  answer: string;                   // AI-generated answer
  sources: RetrievedDocument[];     // Supporting documents
}
```

### Example Request

```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the principles of data processing?", "top_k": 3}'
```

---

## UI Components

### Required Components

| Component | Description |
|-----------|-------------|
| `ChatContainer` | Main wrapper for the chat interface |
| `MessageList` | Displays conversation history |
| `MessageBubble` | Individual message (user or assistant) |
| `ChatInput` | Text input with submit button |
| `SourceCard` | Displays a single source document |
| `SourcesList` | Collapsible list of sources for a response |
| `LoadingIndicator` | Spinner/skeleton while waiting for response |

### Component Hierarchy

```
<App>
  └── <ChatContainer>
        ├── <Header />
        ├── <MessageList>
        │     └── <MessageBubble>
        │           └── <SourcesList>
        │                 └── <SourceCard />
        └── <ChatInput />
```

---

## User Flow

```
1. User lands on chat page
2. User types a question in the input field
3. User clicks "Send" or presses Enter
4. UI shows loading state
5. Response appears with answer text
6. User can expand "Sources" to see citations
7. User can ask follow-up questions
```

---

## UI/UX Requirements

### Layout
- Single-page application
- Chat occupies full viewport height
- Input fixed at bottom
- Messages scroll within container

### Message Display
- User messages aligned right, distinct color
- Assistant messages aligned left
- Timestamps optional but recommended
- Source citations collapsible under each assistant message

### Source Cards
- Show article number prominently
- Display relevance score as percentage badge
- Truncate long text with "Show more" toggle
- Visual hierarchy: article number > score > text

### Responsive Design
- Mobile-first approach
- Works on screens 320px and up
- Input and send button accessible on mobile

---

## State Management

### Local State (useState)

```typescript
// Conversation messages
const [messages, setMessages] = useState<Message[]>([]);

// Current input value
const [input, setInput] = useState('');

// Loading state
const [isLoading, setIsLoading] = useState(false);

// Error state
const [error, setError] = useState<string | null>(null);
```

### Message Type

```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: RetrievedDocument[];
  timestamp: Date;
}
```

---

## Error Handling

| Scenario | User Feedback |
|----------|---------------|
| Network error | "Unable to connect. Please check your connection." |
| Server error (500) | "Something went wrong. Please try again." |
| Empty query | Disable send button, show validation hint |
| Timeout | "Request timed out. Please try again." |

---

## Optional Enhancements

### Phase 2 Features
- [ ] Conversation history persistence (localStorage)
- [ ] Dark/light theme toggle
- [ ] Copy answer to clipboard
- [ ] "Regenerate" response button
- [ ] Adjustable `top_k` setting via UI slider (1-10)

### Phase 3 Features
- [ ] Multiple conversation threads
- [ ] Export conversation as PDF/Markdown
- [ ] Feedback buttons (thumbs up/down)
- [ ] Source document deep links

---

## Environment Configuration

```env
VITE_API_BASE_URL=http://localhost:8080
```

For production, point to the deployed Cloud Run service URL.

---

## File Structure

```
src/
├── components/
│   ├── ChatContainer.tsx
│   ├── ChatInput.tsx
│   ├── MessageBubble.tsx
│   ├── MessageList.tsx
│   ├── SourceCard.tsx
│   ├── SourcesList.tsx
│   └── LoadingIndicator.tsx
├── hooks/
│   └── useChat.ts          # Chat API logic
├── types/
│   └── index.ts            # TypeScript interfaces
├── services/
│   └── api.ts              # API client
├── App.tsx
├── main.tsx
└── index.css               # Tailwind imports
```

---

## Getting Started

```bash
# Create project
npm create vite@latest ai-research-assistant-frontend -- --template react-ts

# Install dependencies
cd ai-research-assistant-frontend
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Start development
npm run dev
```

---

## Design Inspiration

The UI should feel like a modern AI chat assistant (similar to ChatGPT, Claude, or Perplexity) with emphasis on:
- Clean, minimal interface
- Clear visual distinction between user and AI messages
- Accessible source citations that don't clutter the main conversation
- Fast, responsive interactions

