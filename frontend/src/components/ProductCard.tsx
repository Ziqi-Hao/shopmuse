"use client";

import type { Product } from "@/lib/api";

function getAmazonSearchUrl(product: Product): string {
  const query = encodeURIComponent(`${product.title} ${product.category}`);
  return `https://www.amazon.com/s?k=${query}`;
}

export default function ProductCard({ product }: { product: Product }) {
  return (
    <a
      href={getAmazonSearchUrl(product)}
      target="_blank"
      rel="noopener noreferrer"
      className="flex flex-col rounded-2xl border border-gray-100 bg-white shadow-sm hover:shadow-lg hover:border-indigo-200 transition-all overflow-hidden w-[190px] shrink-0 cursor-pointer group"
    >
      <div className="relative h-[150px] bg-gray-50 overflow-hidden">
        <img
          src={product.image_url}
          alt={product.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          loading="lazy"
        />
        <span className="absolute top-2 right-2 bg-white/95 text-[10px] font-semibold px-2 py-0.5 rounded-full text-gray-500 shadow-sm">
          {product.id}
        </span>
        <div className="absolute inset-x-0 bottom-0 h-8 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        <span className="absolute bottom-1.5 left-2 text-white text-[10px] font-medium opacity-0 group-hover:opacity-100 transition-opacity drop-shadow-sm">
          View on Amazon &rarr;
        </span>
      </div>
      <div className="p-2.5 flex flex-col gap-1">
        <h3 className="text-xs font-semibold text-gray-900 leading-snug line-clamp-2 group-hover:text-indigo-600 transition-colors">
          {product.title}
        </h3>
        <div className="flex items-center justify-between">
          <span className="text-sm font-bold text-indigo-600">
            ${product.price.toFixed(2)}
          </span>
          <span className="text-[10px] text-gray-400">{product.brand}</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="flex">
            {[1, 2, 3, 4, 5].map((star) => (
              <svg
                key={star}
                className={`w-3 h-3 ${star <= Math.round(product.rating) ? "text-amber-400" : "text-gray-200"}`}
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
            ))}
          </div>
          <span className="text-[10px] text-gray-400">{product.rating}</span>
        </div>
      </div>
    </a>
  );
}
