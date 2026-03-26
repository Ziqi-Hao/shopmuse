"use client";

import type { ChatMessage as ChatMessageType } from "@/lib/api";
import ProductCard from "./ProductCard";
import ReactMarkdown from "react-markdown";

export default function ChatMessage({ message }: { message: ChatMessageType }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[85%] ${
          isUser
            ? "bg-indigo-600 text-white rounded-2xl rounded-br-md"
            : "bg-white border border-gray-200 text-gray-900 rounded-2xl rounded-bl-md"
        } px-4 py-3 shadow-sm`}
      >
        {/* Show uploaded image if present */}
        {message.image_base64 && (
          <div className="mb-2">
            <img
              src={`data:image/jpeg;base64,${message.image_base64}`}
              alt="Uploaded"
              className="max-w-[200px] rounded-lg"
            />
          </div>
        )}

        {/* Message text with Markdown rendering */}
        <div className="text-sm leading-relaxed prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1 prose-ol:my-1 prose-li:my-0.5 prose-headings:my-2 prose-strong:font-semibold">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {/* Product cards */}
        {message.products && message.products.length > 0 && (
          <div className="mt-3 flex gap-3 overflow-x-auto pb-2 -mx-1 px-1">
            {message.products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
