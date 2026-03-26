"use client";

import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from "react";
import type { ChatMessage as ChatMessageType } from "@/lib/api";
import { sendChatMessage } from "@/lib/api";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";

const WELCOME_MESSAGE: ChatMessageType = {
  role: "assistant",
  content:
    "Hi there! I'm **ShopMuse**, your AI shopping assistant.\n\n" +
    "I can help you in three ways:\n\n" +
    "1. **Describe** what you're looking for and I'll find the best matches\n" +
    "2. **Upload a photo** and I'll search for similar items\n" +
    "3. **Ask** me anything about style, sizing, or outfit ideas\n\n" +
    "What are you shopping for today?",
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
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error. Please make sure the backend server is running.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useImperativeHandle(ref, () => ({
    sendMessage: (msg: string) => handleSend(msg),
  }));

  return (
    <div className="flex flex-col h-full bg-[#f0f2f5]">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 px-6 py-3.5 flex items-center gap-3 shadow-sm">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm shadow-md shadow-indigo-200">
          S
        </div>
        <div className="flex-1">
          <h1 className="text-[15px] font-semibold text-gray-900">ShopMuse</h1>
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-green-400" />
            <p className="text-[11px] text-gray-400">Online</p>
          </div>
        </div>
        {/* Mobile: show on small screens */}
        <span className="lg:hidden text-[11px] text-gray-400 bg-gray-50 px-2.5 py-1 rounded-full">
          100 products
        </span>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 md:px-8 lg:px-12">
        <div className="max-w-3xl mx-auto">
          {messages.map((msg, idx) => (
            <ChatMessage key={idx} message={msg} />
          ))}

          {loading && (
            <div className="flex items-start gap-3 mb-4">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs shrink-0 mt-0.5">
                S
              </div>
              <div className="bg-white border border-gray-100 rounded-2xl rounded-tl-md px-4 py-3 shadow-sm">
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 bg-indigo-400 rounded-full animate-pulse-soft" />
                  <div className="w-2 h-2 bg-indigo-400 rounded-full animate-pulse-soft" style={{ animationDelay: "200ms" }} />
                  <div className="w-2 h-2 bg-indigo-400 rounded-full animate-pulse-soft" style={{ animationDelay: "400ms" }} />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <ChatInput onSend={handleSend} disabled={loading} />
    </div>
  );
});

export default ChatWindow;
