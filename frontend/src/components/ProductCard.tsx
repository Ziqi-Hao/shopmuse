"use client";

import { useState } from "react";
import type { Product } from "@/lib/api";

export default function ProductCard({ product }: { product: Product }) {
  const [showDetail, setShowDetail] = useState(false);

  const discountedPrice = product.discount_pct
    ? product.price * (1 - product.discount_pct / 100)
    : null;

  return (
    <>
      <div
        onClick={() => setShowDetail(true)}
        className="flex flex-col rounded-xl border border-slate-200/80 bg-white hover:shadow-md hover:border-indigo-200 transition-all overflow-hidden w-[172px] shrink-0 cursor-pointer group"
      >
        <div className="relative h-[140px] bg-slate-50 overflow-hidden">
          <img
            src={product.image_url}
            alt={product.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
          {product.discount_pct ? (
            <span className="absolute top-1.5 left-1.5 bg-rose-500 text-white text-[9px] font-bold px-1.5 py-0.5 rounded-md">
              -{product.discount_pct}%
            </span>
          ) : null}
          {product.in_stock === false && (
            <div className="absolute inset-0 bg-slate-900/40 flex items-center justify-center">
              <span className="text-white text-[10px] font-medium bg-slate-900/70 px-2 py-0.5 rounded">Sold Out</span>
            </div>
          )}
        </div>
        <div className="p-2.5 flex flex-col gap-1">
          <p className="text-[10px] text-slate-400 font-medium">{product.brand}</p>
          <h3 className="text-[12px] font-semibold text-slate-800 leading-tight line-clamp-2 group-hover:text-indigo-600 transition-colors">
            {product.title}
          </h3>
          <div className="flex items-center gap-1.5 mt-0.5">
            {discountedPrice ? (
              <>
                <span className="text-sm font-bold text-rose-600">${discountedPrice.toFixed(2)}</span>
                <span className="text-[10px] text-slate-400 line-through">${product.price.toFixed(2)}</span>
              </>
            ) : (
              <span className="text-sm font-bold text-slate-800">${product.price.toFixed(2)}</span>
            )}
          </div>
          <div className="flex items-center gap-1">
            <div className="flex">
              {[1, 2, 3, 4, 5].map((s) => (
                <svg key={s} className={`w-2.5 h-2.5 ${s <= Math.round(product.rating) ? "text-amber-400" : "text-slate-200"}`} fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              ))}
            </div>
            <span className="text-[9px] text-slate-400">
              {product.review_count ? `(${product.review_count})` : product.rating}
            </span>
          </div>
        </div>
      </div>

      {/* Detail Modal */}
      {showDetail && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={() => setShowDetail(false)}>
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="h-64 bg-slate-100 relative">
              <img src={product.image_url} alt={product.title} className="w-full h-full object-cover" />
              <button onClick={() => setShowDetail(false)} className="absolute top-3 right-3 w-8 h-8 bg-white/90 backdrop-blur rounded-full flex items-center justify-center text-slate-500 hover:text-slate-800 shadow">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" /></svg>
              </button>
              {product.discount_pct ? (
                <span className="absolute top-3 left-3 bg-rose-500 text-white text-xs font-bold px-2.5 py-1 rounded-lg shadow">
                  {product.discount_pct}% OFF
                </span>
              ) : null}
            </div>

            <div className="p-6">
              <p className="text-xs text-slate-400 font-medium mb-1">{product.brand} &middot; {product.id}</p>
              <h2 className="text-xl font-bold text-slate-900 mb-1">{product.title}</h2>

              <div className="flex items-center gap-2 mb-4">
                {discountedPrice ? (
                  <>
                    <span className="text-2xl font-bold text-rose-600">${discountedPrice.toFixed(2)}</span>
                    <span className="text-sm text-slate-400 line-through">${product.price.toFixed(2)}</span>
                  </>
                ) : (
                  <span className="text-2xl font-bold text-slate-900">${product.price.toFixed(2)}</span>
                )}
                <span className="ml-auto">
                  {product.in_stock === false ? (
                    <span className="text-[11px] font-medium text-rose-600 bg-rose-50 px-2.5 py-1 rounded-full">Out of Stock</span>
                  ) : (
                    <span className="text-[11px] font-medium text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full">In Stock</span>
                  )}
                </span>
              </div>

              <p className="text-sm text-slate-600 leading-relaxed mb-5">{product.description}</p>

              <div className="grid grid-cols-2 gap-2 text-xs mb-4">
                {[
                  ["Color", product.color],
                  ["Material", product.material || "N/A"],
                  ["Style", product.style],
                  ["Use Case", product.use_case],
                ].map(([label, value]) => (
                  <div key={label} className="bg-slate-50 rounded-lg px-3 py-2">
                    <span className="text-slate-400 text-[10px]">{label}</span>
                    <p className="font-medium text-slate-700 capitalize">{value}</p>
                  </div>
                ))}
              </div>

              {product.sizes && product.sizes.length > 1 && (
                <div className="mb-4">
                  <p className="text-[10px] text-slate-400 mb-1.5 font-medium">Sizes</p>
                  <div className="flex flex-wrap gap-1.5">
                    {product.sizes.map((size) => (
                      <span key={size} className="text-[11px] px-2.5 py-1 rounded-lg border border-slate-200 text-slate-600 hover:border-indigo-300 hover:text-indigo-600 cursor-pointer transition-colors">{size}</span>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex flex-wrap gap-1.5 mb-4">
                {product.tags.map((tag) => (
                  <span key={tag} className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-600 font-medium">{tag}</span>
                ))}
              </div>

              <div className="flex items-center gap-2 pt-3 border-t border-slate-100">
                <div className="flex">
                  {[1, 2, 3, 4, 5].map((s) => (
                    <svg key={s} className={`w-4 h-4 ${s <= Math.round(product.rating) ? "text-amber-400" : "text-slate-200"}`} fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
                <span className="text-sm text-slate-600 font-medium">{product.rating}</span>
                {product.review_count ? (
                  <span className="text-xs text-slate-400">({product.review_count.toLocaleString()} reviews)</span>
                ) : null}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
