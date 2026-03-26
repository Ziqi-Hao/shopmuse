const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Product {
  id: string;
  title: string;
  category: string;
  description: string;
  tags: string[];
  price: number;
  color: string;
  style: string;
  use_case: string;
  gender: string;
  rating: number;
  brand: string;
  image_url: string;
  material?: string;
  sizes?: string[];
  in_stock?: boolean;
  review_count?: number;
  discount_pct?: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  products?: Product[];
  image_base64?: string;
}

export interface ChatResponse {
  message: string;
  products?: Product[];
  intent: string;
}

// Generate a persistent session ID per browser tab
let _sessionId: string | null = null;
export function getSessionId(): string {
  if (!_sessionId) {
    _sessionId = `session_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
  }
  return _sessionId;
}

export async function sendChatMessage(
  message: string,
  history: ChatMessage[],
  imageBase64?: string
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      image_base64: imageBase64 || null,
      session_id: getSessionId(),
      history: history.map((m) => ({
        role: m.role,
        content: m.content,
      })),
    }),
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json();
}
