"use client";

/**
 * Lightweight Markdown renderer for chat messages.
 * Handles: **bold**, *italic*, - lists, 1. ordered lists, \n\n paragraphs
 * No heavy dependencies needed.
 */
export default function MarkdownContent({ content }: { content: string }) {
  const paragraphs = content.split(/\n\n+/);

  return (
    <div className="space-y-2">
      {paragraphs.map((para, i) => (
        <Paragraph key={i} text={para.trim()} />
      ))}
    </div>
  );
}

function Paragraph({ text }: { text: string }) {
  // Check if it's a list block (lines starting with - or * or 1.)
  const lines = text.split("\n");
  const isUnorderedList = lines.every(
    (l) => l.trim().startsWith("- ") || l.trim().startsWith("* ") || l.trim() === ""
  );
  const isOrderedList = lines.every(
    (l) => /^\d+[\.\)]\s/.test(l.trim()) || l.trim() === ""
  );

  if (isUnorderedList && lines.some((l) => l.trim().startsWith("- ") || l.trim().startsWith("* "))) {
    return (
      <ul className="list-disc list-inside space-y-1 ml-1">
        {lines
          .filter((l) => l.trim())
          .map((line, j) => (
            <li key={j} className="text-sm leading-relaxed">
              <InlineMarkdown text={line.replace(/^\s*[-*]\s+/, "")} />
            </li>
          ))}
      </ul>
    );
  }

  if (isOrderedList && lines.some((l) => /^\d+[\.\)]\s/.test(l.trim()))) {
    return (
      <ol className="list-decimal list-inside space-y-1 ml-1">
        {lines
          .filter((l) => l.trim())
          .map((line, j) => (
            <li key={j} className="text-sm leading-relaxed">
              <InlineMarkdown text={line.replace(/^\s*\d+[\.\)]\s+/, "")} />
            </li>
          ))}
      </ol>
    );
  }

  // Check for lines that contain sub-items (indented with *)
  const hasSubItems = lines.some((l) => /^\s+\*\s/.test(l));
  if (hasSubItems) {
    return (
      <div className="space-y-1">
        {lines.map((line, j) => {
          const trimmed = line.trim();
          if (!trimmed) return null;
          if (/^\*\s/.test(trimmed)) {
            return (
              <div key={j} className="ml-4 text-sm leading-relaxed flex gap-1.5">
                <span className="text-gray-400 shrink-0">&#8226;</span>
                <InlineMarkdown text={trimmed.replace(/^\*\s+/, "")} />
              </div>
            );
          }
          return (
            <p key={j} className="text-sm leading-relaxed">
              <InlineMarkdown text={trimmed} />
            </p>
          );
        })}
      </div>
    );
  }

  // Regular paragraph (may contain line breaks)
  return (
    <p className="text-sm leading-relaxed">
      {lines.map((line, j) => (
        <span key={j}>
          {j > 0 && <br />}
          <InlineMarkdown text={line} />
        </span>
      ))}
    </p>
  );
}

function InlineMarkdown({ text }: { text: string }) {
  // Parse inline markdown: **bold**, *italic*, `code`
  const parts: React.ReactNode[] = [];
  let remaining = text;
  let key = 0;

  while (remaining.length > 0) {
    // Bold: **text**
    const boldMatch = remaining.match(/\*\*(.+?)\*\*/);
    // Italic: *text* (but not **)
    const italicMatch = remaining.match(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/);
    // Code: `text`
    const codeMatch = remaining.match(/`(.+?)`/);

    // Find the earliest match
    const matches = [
      boldMatch ? { type: "bold", match: boldMatch } : null,
      italicMatch ? { type: "italic", match: italicMatch } : null,
      codeMatch ? { type: "code", match: codeMatch } : null,
    ]
      .filter(Boolean)
      .sort((a, b) => (a!.match.index ?? 0) - (b!.match.index ?? 0));

    if (matches.length === 0) {
      parts.push(<span key={key++}>{remaining}</span>);
      break;
    }

    const first = matches[0]!;
    const idx = first.match.index ?? 0;

    // Add text before the match
    if (idx > 0) {
      parts.push(<span key={key++}>{remaining.slice(0, idx)}</span>);
    }

    // Add the formatted text
    if (first.type === "bold") {
      parts.push(
        <strong key={key++} className="font-semibold">
          {first.match[1]}
        </strong>
      );
    } else if (first.type === "italic") {
      parts.push(
        <em key={key++} className="italic">
          {first.match[1]}
        </em>
      );
    } else if (first.type === "code") {
      parts.push(
        <code key={key++} className="bg-gray-100 text-indigo-700 px-1 py-0.5 rounded text-xs font-mono">
          {first.match[1]}
        </code>
      );
    }

    remaining = remaining.slice(idx + first.match[0].length);
  }

  return <>{parts}</>;
}
