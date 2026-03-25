"use client";

import type { Product } from "@/lib/api";

export default function ProductCard({ product }: { product: Product }) {
  return (
    <div className="flex flex-col rounded-xl border border-gray-200 bg-white shadow-sm hover:shadow-md transition-shadow overflow-hidden w-[200px] shrink-0">
      <div className="relative h-[160px] bg-gray-100">
        <img
          src={product.image_url}
          alt={product.title}
          className="w-full h-full object-cover"
          loading="lazy"
        />
        <span className="absolute top-2 right-2 bg-white/90 text-xs font-semibold px-2 py-0.5 rounded-full text-gray-700">
          {product.id}
        </span>
      </div>
      <div className="p-3 flex flex-col gap-1.5">
        <h3 className="text-sm font-semibold text-gray-900 leading-tight line-clamp-2">
          {product.title}
        </h3>
        <div className="flex items-center justify-between">
          <span className="text-base font-bold text-indigo-600">
            ${product.price.toFixed(2)}
          </span>
          <span className="text-xs text-gray-500">{product.brand}</span>
        </div>
        <div className="flex flex-wrap gap-1 mt-1">
          <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700">
            {product.category}
          </span>
          <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-gray-100 text-gray-600">
            {product.style}
          </span>
        </div>
        <div className="flex items-center gap-1 mt-0.5">
          <span className="text-yellow-500 text-xs">{"★".repeat(Math.round(product.rating))}</span>
          <span className="text-[10px] text-gray-400">{product.rating}</span>
        </div>
      </div>
    </div>
  );
}
