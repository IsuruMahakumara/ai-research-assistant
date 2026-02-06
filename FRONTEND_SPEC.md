# Frontend Build Instructions

Build a chat frontend for this backend. Use React + Vite + TypeScript.

## Backend API

The backend runs at `http://localhost:8080` with these endpoints:

### POST /chat

Send a question, get an AI answer with sources.

**Request:**
```json
{
  "query": "What are the GDPR principles?",
  "top_k": 3
}
```

**Response:**
```json
{
  "query": "What are the GDPR principles?",
  "answer": "The GDPR establishes several key principles...",
  "sources": [
    {
      "id": "doc-123",
      "article_num": "Article 5",
      "text": "Personal data shall be processed lawfully...",
      "score": 0.92
    }
  ]
}
```

### GET /

Health check. Returns `{"status": "alive"}`.

## Requirements

1. User can type a question and submit it
2. Display the AI's answer
3. Show source citations (article number, relevance score, text preview)
4. Handle loading state while waiting for response
5. Handle errors gracefully

## Constraints

- Use `npm create vite@latest` with `react-ts` template
- Keep it simple - single page app is fine
- Style it however you think looks good

## Notes

- The `top_k` parameter is optional (defaults to 3)
- Source scores are 0-1 (higher = more relevant)
- Backend may take a few seconds to respond
