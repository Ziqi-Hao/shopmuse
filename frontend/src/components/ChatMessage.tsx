"use client";

import type { ChatMessage as ChatMessageType } from "@/lib/api";
import ProductCard from "./ProductCard";
import MarkdownContent from "./MarkdownContent";

export default function ChatMessage({ message }: { message: ChatMessageType }) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end mb-5">
        <div className="max-w-[75%] bg-indigo-600 text-white rounded-2xl rounded-br-sm px-4 py-3 shadow-md shadow-indigo-200/50">
          {message.image_base64 && (
            <div className="mb-2">
              <img
                src={`data:image/jpeg;base64,${message.image_base64}`}
                alt="Uploaded"
                className="max-w-[200px] rounded-lg"
              />
            </div>
          )}
          <p className="text-sm leading-relaxed">{message.content}</p>
        </div>
      </div>
    );
  }

  // Assistant message
  return (
    <div className="flex items-start gap-3 mb-5">
      <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-xs shrink-0 mt-0.5 shadow-md shadow-indigo-200/50">
        S
      </div>
      <div className="max-w-[85%] min-w-0">
        <div className="bg-white border border-gray-100 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
          <MarkdownContent content={message.content} />
        </div>

        {/* Product cards */}
        {message.products && message.products.length > 0 && (
          <div className="mt-3 flex gap-3 overflow-x-auto pb-2 product-scroll">
            {message.products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
