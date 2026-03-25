"use client";

import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from "react";
import type { ChatMessage as ChatMessageType } from "@/lib/api";
import { sendChatMessage } from "@/lib/api";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";

const WELCOME_MESSAGE: ChatMessageType = {
  role: "assistant",
  content:
    "Hi! I'm ShopMuse, your AI shopping assistant. I can help you:\n\n" +
    "- Find products based on what you describe\n" +
    "- Search for similar items when you upload an image\n" +
    "- Answer questions about our catalog\n\n" +
    "What are you looking for today?",
};

export interface ChatWindowHandle {
  sendMessage: (msg: string) => void;
}

const ChatWindow = forwardRef<ChatWindowHandle>(function ChatWindow(_, ref) {
  const [messages, setMessages] = useState<ChatMessageType[]>([WELCOME_MESSAGE]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (message: string, imageBase64?: string) => {
    const userMessage: ChatMessageType = {
      role: "user",
      content: message,
      image_base64: imageBase64,
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await sendChatMessage(message, messages, imageBase64);

      const assistantMessage: ChatMessageType = {
        role: "assistant",
        content: response.message,
        products: response.products || undefined,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessageType = {
        role: "assistant",
        content:
          "Sorry, I encountered an error. Please make sure the backend server is running on port 8000.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  useImperativeHandle(ref, () => ({
    sendMessage: (msg: string) => handleSend(msg),
  }));

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white px-6 py-4 flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg">
          S
        </div>
        <div>
          <h1 className="text-lg font-semibold text-gray-900">ShopMuse</h1>
          <p className="text-xs text-gray-500">AI Shopping Assistant</p>
        </div>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {messages.map((msg, idx) => (
          <ChatMessage key={idx} message={msg} />
        ))}

        {loading && (
          <div className="flex justify-start mb-4">
            <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
              <div className="flex items-center gap-1.5">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={handleSend} disabled={loading} />
    </div>
  );
});

export default ChatWindow;
