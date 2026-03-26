"use client";

import type { ChatMessage as ChatMessageType } from "@/lib/api";
import ProductCard from "./ProductCard";
import MarkdownContent from "./MarkdownContent";
import Logo from "./Logo";

export default function ChatMessage({ message }: { message: ChatMessageType }) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end py-2">
        <div className="max-w-[75%]">
          {message.image_base64 && (
            <div className="mb-2 flex justify-end">
              <img
                src={`data:image/jpeg;base64,${message.image_base64}`}
                alt="Uploaded"
                className="max-w-[180px] rounded-xl shadow-sm"
              />
            </div>
          )}
          <div className="bg-indigo-600 text-white rounded-2xl rounded-br-sm px-4 py-2.5 shadow-sm">
            <p className="text-[13px] leading-relaxed">{message.content}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-3 py-3">
      <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
        <Logo size={16} />
      </div>
      <div className="max-w-[88%] min-w-0 space-y-3">
        <div className="bg-white border border-slate-200/60 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
          <MarkdownContent content={message.content} />
        </div>

        {message.products && message.products.length > 0 && (
          <div className="flex gap-3 overflow-x-auto pb-1 product-scroll -ml-1 pl-1">
            {message.products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
