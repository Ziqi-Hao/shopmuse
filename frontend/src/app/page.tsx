"use client";

import ChatWindow, { type ChatWindowHandle } from "@/components/ChatWindow";
import { useRef } from "react";

export default function Home() {
  const chatRef = useRef<ChatWindowHandle>(null);

  const handleSuggestion = (suggestion: string) => {
    chatRef.current?.sendMessage(suggestion);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="hidden md:flex w-64 flex-col bg-white border-r border-gray-200">
        <div className="p-6">
          <h2 className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            ShopMuse
          </h2>
          <p className="text-xs text-gray-500 mt-1">Multimodal Shopping Agent</p>
        </div>

        <nav className="flex-1 px-4 space-y-1">
          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 mb-2">
            Try asking
          </div>
          {[
            "Recommend a casual t-shirt",
            "Find waterproof hiking boots",
            "Show me bags for office use",
            "I need sporty pants under $50",
            "Suggest a warm winter jacket",
          ].map((suggestion) => (
            <button
              key={suggestion}
              className="w-full text-left text-sm text-gray-600 hover:bg-indigo-50 hover:text-indigo-700 rounded-lg px-3 py-2 transition-colors"
              onClick={() => handleSuggestion(suggestion)}
            >
              {suggestion}
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-400 space-y-1">
            <p>Upload an image to search visually</p>
            <p>100 products across 6 categories</p>
          </div>
        </div>
      </aside>

      {/* Main chat area */}
      <main className="flex-1 flex flex-col min-w-0">
        <ChatWindow ref={chatRef} />
      </main>
    </div>
  );
}
