"use client";

export default function Logo({ size = 36 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Shopping bag body */}
      <rect x="8" y="16" width="32" height="28" rx="4" fill="url(#bag-gradient)" />
      {/* Bag handles */}
      <path
        d="M16 16V12C16 7.58 19.58 4 24 4C28.42 4 32 7.58 32 12V16"
        stroke="url(#handle-gradient)"
        strokeWidth="3"
        strokeLinecap="round"
        fill="none"
      />
      {/* Sparkle / AI star - top right */}
      <path
        d="M38 8L39.5 11.5L43 13L39.5 14.5L38 18L36.5 14.5L33 13L36.5 11.5L38 8Z"
        fill="#a78bfa"
      />
      {/* Small sparkle */}
      <path
        d="M42 3L42.8 5.2L45 6L42.8 6.8L42 9L41.2 6.8L39 6L41.2 5.2L42 3Z"
        fill="#c4b5fd"
        opacity="0.7"
      />
      {/* Search magnifier on bag */}
      <circle cx="22" cy="30" r="5" stroke="white" strokeWidth="2" fill="none" opacity="0.9" />
      <path d="M26 34L30 38" stroke="white" strokeWidth="2" strokeLinecap="round" opacity="0.9" />
      <defs>
        <linearGradient id="bag-gradient" x1="8" y1="16" x2="40" y2="44" gradientUnits="userSpaceOnUse">
          <stop stopColor="#6366f1" />
          <stop offset="1" stopColor="#8b5cf6" />
        </linearGradient>
        <linearGradient id="handle-gradient" x1="16" y1="4" x2="32" y2="16" gradientUnits="userSpaceOnUse">
          <stop stopColor="#6366f1" />
          <stop offset="1" stopColor="#a78bfa" />
        </linearGradient>
      </defs>
    </svg>
  );
}

export function LogoMark({ className = "" }: { className?: string }) {
  return (
    <div className={`flex items-center gap-2.5 ${className}`}>
      <Logo size={32} />
      <div>
        <span className="text-lg font-bold tracking-tight text-gray-900">
          Shop<span className="text-indigo-600">Muse</span>
        </span>
      </div>
    </div>
  );
}
