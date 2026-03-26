"use client";

import { useState } from "react";
import type { Product } from "@/lib/api";

export default function ProductCard({ product }: { product: Product }) {
  const [showDetail, setShowDetail] = useState(false);

  return (
    <>
      <div
        onClick={() => setShowDetail(true)}
        className="flex flex-col rounded-2xl border border-gray-100 bg-white shadow-sm hover:shadow-lg hover:border-indigo-200 transition-all overflow-hidden w-[190px] shrink-0 cursor-pointer group"
      >
        <div className="relative h-[150px] bg-gray-50 overflow-hidden">
          <img
            src={product.image_url}
            alt={product.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
          {product.discount_pct ? (
            <span className="absolute top-2 left-2 bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full shadow-sm">
              -{product.discount_pct}%
            </span>
          ) : null}
          {product.in_stock === false && (
            <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
              <span className="text-white text-xs font-semibold bg-black/60 px-2 py-1 rounded">Out of Stock</span>
            </div>
          )}
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
      </div>

      {/* Detail Modal */}
      {showDetail && (
        <div
          className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setShowDetail(false)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="h-56 bg-gray-100 relative">
              <img
                src={product.image_url}
                alt={product.title}
                className="w-full h-full object-cover"
              />
              <button
                onClick={() => setShowDetail(false)}
                className="absolute top-3 right-3 w-8 h-8 bg-white/90 rounded-full flex items-center justify-center text-gray-500 hover:text-gray-800 shadow-sm"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-5">
              <div className="flex items-start justify-between gap-3 mb-1">
                <h2 className="text-lg font-bold text-gray-900">{product.title}</h2>
                <div className="text-right shrink-0">
                  {product.discount_pct ? (
                    <>
                      <span className="text-xs text-red-500 font-medium bg-red-50 px-1.5 py-0.5 rounded">-{product.discount_pct}%</span>
                      <p className="text-xl font-bold text-indigo-600">${product.price.toFixed(2)}</p>
                    </>
                  ) : (
                    <span className="text-xl font-bold text-indigo-600">${product.price.toFixed(2)}</span>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2 mb-3">
                {product.in_stock === false ? (
                  <span className="text-[11px] font-medium text-red-600 bg-red-50 px-2 py-0.5 rounded-full">Out of Stock</span>
                ) : (
                  <span className="text-[11px] font-medium text-green-600 bg-green-50 px-2 py-0.5 rounded-full">In Stock</span>
                )}
                {product.review_count !== undefined && (
                  <span className="text-[11px] text-gray-400">{product.review_count.toLocaleString()} reviews</span>
                )}
              </div>

              <p className="text-sm text-gray-600 mb-4 leading-relaxed">
                {product.description}
              </p>

              <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                <div className="bg-gray-50 rounded-lg px-3 py-2">
                  <span className="text-gray-400">Brand</span>
                  <p className="font-medium text-gray-700">{product.brand}</p>
                </div>
                <div className="bg-gray-50 rounded-lg px-3 py-2">
                  <span className="text-gray-400">Color</span>
                  <p className="font-medium text-gray-700">{product.color}</p>
                </div>
                <div className="bg-gray-50 rounded-lg px-3 py-2">
                  <span className="text-gray-400">Material</span>
                  <p className="font-medium text-gray-700">{product.material || "N/A"}</p>
                </div>
                <div className="bg-gray-50 rounded-lg px-3 py-2">
                  <span className="text-gray-400">Style</span>
                  <p className="font-medium text-gray-700">{product.style}</p>
                </div>
              </div>

              {product.sizes && product.sizes.length > 1 && (
                <div className="mb-3">
                  <span className="text-[11px] text-gray-400 mb-1 block">Available Sizes</span>
                  <div className="flex flex-wrap gap-1">
                    {product.sizes.map((size) => (
                      <span key={size} className="text-[11px] px-2 py-0.5 rounded border border-gray-200 text-gray-600">{size}</span>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex flex-wrap gap-1.5 mb-4">
                {product.tags.map((tag) => (
                  <span
                    key={tag}
                    className="text-[11px] px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-600"
                  >
                    {tag}
                  </span>
                ))}
              </div>

              <div className="flex items-center gap-1.5">
                <div className="flex">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <svg
                      key={star}
                      className={`w-4 h-4 ${star <= Math.round(product.rating) ? "text-amber-400" : "text-gray-200"}`}
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
                <span className="text-sm text-gray-500">{product.rating} rating</span>
                <span className="text-xs text-gray-300 mx-1">|</span>
                <span className="text-xs text-gray-400">{product.category}</span>
                <span className="text-xs text-gray-400">| {product.gender}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
