"use client";

import ChatWindow, { type ChatWindowHandle } from "@/components/ChatWindow";
import { LogoMark } from "@/components/Logo";
import { useRef } from "react";

const SUGGESTIONS = [
  { icon: "👕", text: "Recommend a casual t-shirt", color: "bg-blue-50 text-blue-700 border-blue-100" },
  { icon: "🥾", text: "Find waterproof hiking boots", color: "bg-emerald-50 text-emerald-700 border-emerald-100" },
  { icon: "💼", text: "Show me bags for office use", color: "bg-amber-50 text-amber-700 border-amber-100" },
  { icon: "🏃", text: "Sporty pants under $50", color: "bg-rose-50 text-rose-700 border-rose-100" },
  { icon: "🧥", text: "Suggest a warm winter jacket", color: "bg-violet-50 text-violet-700 border-violet-100" },
  { icon: "⌚", text: "Accessories for a gift", color: "bg-teal-50 text-teal-700 border-teal-100" },
];

export default function Home() {
  const chatRef = useRef<ChatWindowHandle>(null);

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="hidden lg:flex w-[280px] flex-col bg-white border-r border-slate-200/80">
        <div className="p-5 pb-4">
          <LogoMark />
          <p className="text-[11px] text-slate-400 mt-1 ml-[42px]">AI-powered shopping assistant</p>
        </div>

        <div className="mx-4 h-px bg-slate-100" />

        <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
          <p className="text-[10px] font-medium text-slate-400 uppercase tracking-widest mb-3 px-1">
            Try these
          </p>
          {SUGGESTIONS.map(({ icon, text, color }) => (
            <button
              key={text}
              className={`w-full text-left text-[13px] rounded-xl px-3 py-2.5 border transition-all flex items-center gap-2.5 hover:shadow-sm active:scale-[0.98] ${color}`}
              onClick={() => chatRef.current?.sendMessage(text)}
            >
              <span className="text-base">{icon}</span>
              <span className="font-medium">{text}</span>
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-100">
          <div className="rounded-xl bg-gradient-to-br from-indigo-50 via-violet-50 to-purple-50 p-4">
            <p className="text-xs font-semibold text-indigo-700 mb-1.5">How it works</p>
            <p className="text-[11px] text-indigo-600/70 leading-relaxed">
              Type what you want or upload a photo. ShopMuse searches 500 products across 6 categories using AI-powered semantic search.
            </p>
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 flex flex-col min-w-0 bg-slate-50">
        <ChatWindow ref={chatRef} />
      </main>
    </div>
  );
}
