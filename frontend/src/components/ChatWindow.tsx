"use client";

import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from "react";
import type { ChatMessage as ChatMessageType } from "@/lib/api";
import { sendChatMessage } from "@/lib/api";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import { LogoMark } from "./Logo";
import Logo from "./Logo";

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
    setMessages((prev) => [
      ...prev,
      { role: "user", content: message, image_base64: imageBase64 },
    ]);
    setLoading(true);

    try {
      const response = await sendChatMessage(message, messages, imageBase64);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.message, products: response.products || undefined },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I couldn't process that. Please make sure the backend is running." },
      ]);
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
      <header className="bg-white/80 backdrop-blur-md border-b border-slate-200/60 px-5 py-3 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <Logo size={28} />
          <div>
            <h1 className="text-sm font-semibold text-slate-800">ShopMuse</h1>
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-[10px] text-slate-400">Ready</span>
            </div>
          </div>
        </div>
        <div className="lg:hidden">
          <span className="text-[10px] text-slate-400 bg-slate-100 px-2.5 py-1 rounded-full font-medium">
            500 products
          </span>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 md:px-6 lg:px-10">
        <div className="max-w-3xl mx-auto space-y-1">
          {messages.map((msg, idx) => (
            <ChatMessage key={idx} message={msg} />
          ))}

          {loading && (
            <div className="flex items-start gap-3 py-3">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center shrink-0">
                <Logo size={16} />
              </div>
              <div className="bg-white border border-slate-200/60 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
                <div className="flex items-center gap-1">
                  <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full typing-dot" />
                  <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full typing-dot" />
                  <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full typing-dot" />
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
