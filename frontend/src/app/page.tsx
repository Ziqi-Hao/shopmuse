"use client";

import ChatWindow, { type ChatWindowHandle } from "@/components/ChatWindow";
import { useRef } from "react";

const SUGGESTIONS = [
  { icon: "👕", text: "Recommend a casual t-shirt" },
  { icon: "🥾", text: "Find waterproof hiking boots" },
  { icon: "💼", text: "Show me bags for office use" },
  { icon: "🏃", text: "I need sporty pants under $50" },
  { icon: "🧥", text: "Suggest a warm winter jacket" },
  { icon: "⌚", text: "Show me accessories for gifts" },
];

export default function Home() {
  const chatRef = useRef<ChatWindowHandle>(null);

  return (
    <div className="flex h-screen bg-[#f0f2f5]">
      {/* Sidebar */}
      <aside className="hidden lg:flex w-72 flex-col bg-white border-r border-gray-100 shadow-sm">
        {/* Brand header */}
        <div className="p-6 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-indigo-200">
              S
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900">ShopMuse</h2>
              <p className="text-[11px] text-gray-400 -mt-0.5">AI Shopping Assistant</p>
            </div>
          </div>
        </div>

        <div className="h-px bg-gray-100 mx-4" />

        {/* Suggestions */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          <div className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest px-3 mb-3">
            Quick prompts
          </div>
          {SUGGESTIONS.map(({ icon, text }) => (
            <button
              key={text}
              className="w-full text-left text-[13px] text-gray-600 hover:bg-gradient-to-r hover:from-indigo-50 hover:to-purple-50 hover:text-indigo-700 rounded-xl px-3 py-2.5 transition-all flex items-center gap-2.5 group"
              onClick={() => chatRef.current?.sendMessage(text)}
            >
              <span className="text-base group-hover:scale-110 transition-transform">{icon}</span>
              <span>{text}</span>
            </button>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-100">
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-3">
            <p className="text-[11px] font-medium text-indigo-700 mb-1">How it works</p>
            <p className="text-[11px] text-indigo-600/70 leading-relaxed">
              Describe what you want or upload a photo. ShopMuse searches 100 products across 6 categories to find the best matches.
            </p>
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
