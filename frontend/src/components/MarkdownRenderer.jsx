import React from 'react';

/**
 * Parses inline markdown tokens: bold (**text**), inline code (`code`), and plain text.
 */
function parseInline(text) {
  if (!text) return text;

  // Split by inline code first
  const codeParts = text.split(/(`[^`]+`)/g);
  return codeParts.map((part, index) => {
    if (part.startsWith('`') && part.endsWith('`') && part.length >= 2) {
      return (
        <code
          key={index}
          className="px-1.5 py-0.5 mx-0.5 text-xs font-mono bg-indigo-950/80 text-indigo-300 border border-indigo-800/50 rounded-md"
        >
          {part.slice(1, -1)}
        </code>
      );
    }

    // Split by bold (**text**)
    const boldParts = part.split(/(\*\*[^*]+\*\*)/g);
    return boldParts.map((bPart, bIndex) => {
      if (bPart.startsWith('**') && bPart.endsWith('**') && bPart.length >= 4) {
        return (
          <strong key={`${index}-${bIndex}`} className="font-semibold text-white">
            {bPart.slice(2, -2)}
          </strong>
        );
      }
      return bPart;
    });
  });
}

/**
 * Lightweight and robust markdown renderer for chat assistant responses.
 */
export default function MarkdownRenderer({ content }) {
  if (!content) return null;

  const lines = content.split('\n');
  const elements = [];
  let currentList = [];

  const flushList = () => {
    if (currentList.length > 0) {
      elements.push(
        <ul key={`list-${elements.length}`} className="my-2.5 space-y-1.5 text-slate-300">
          {currentList.map((item, idx) => (
            <li key={idx} className="flex items-start gap-2 text-sm leading-relaxed">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-2 flex-shrink-0" />
              <span>{parseInline(item)}</span>
            </li>
          ))}
        </ul>
      );
      currentList = [];
    }
  };

  lines.forEach((line, index) => {
    const trimmed = line.trim();

    // Horizontal Rule
    if (trimmed === '---' || trimmed === '***') {
      flushList();
      elements.push(
        <hr key={`hr-${index}`} className="my-3 border-t border-slate-700/60" />
      );
      return;
    }

    // Headings: ### Heading 3
    if (trimmed.startsWith('### ')) {
      flushList();
      elements.push(
        <h3
          key={`h3-${index}`}
          className="text-sm font-bold text-indigo-300 uppercase tracking-wide mt-3.5 mb-1.5 flex items-center gap-1.5"
        >
          <span className="w-1.5 h-3.5 bg-indigo-500 rounded-sm inline-block" />
          {parseInline(trimmed.slice(4))}
        </h3>
      );
      return;
    }

    // Headings: ## Heading 2
    if (trimmed.startsWith('## ')) {
      flushList();
      elements.push(
        <h2
          key={`h2-${index}`}
          className="text-base font-bold text-white mt-4 mb-2 border-b border-slate-700/50 pb-1"
        >
          {parseInline(trimmed.slice(3))}
        </h2>
      );
      return;
    }

    // Headings: # Heading 1
    if (trimmed.startsWith('# ')) {
      flushList();
      elements.push(
        <h1 key={`h1-${index}`} className="text-lg font-extrabold text-white mt-4 mb-2">
          {parseInline(trimmed.slice(2))}
        </h1>
      );
      return;
    }

    // Bullet item (* or -)
    if (trimmed.startsWith('* ') || trimmed.startsWith('- ')) {
      currentList.push(trimmed.slice(2));
      return;
    }

    // Numbered list item: 1. Item
    const numMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
    if (numMatch) {
      flushList();
      elements.push(
        <div key={`num-${index}`} className="flex items-start gap-2.5 my-1.5 text-sm leading-relaxed text-slate-300">
          <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-indigo-900/60 text-indigo-300 border border-indigo-700/40 flex-shrink-0 mt-0.5">
            {numMatch[1]}
          </span>
          <div>{parseInline(numMatch[2])}</div>
        </div>
      );
      return;
    }

    // Normal text or empty line
    flushList();
    if (trimmed === '') {
      elements.push(<div key={`empty-${index}`} className="h-2" />);
    } else {
      elements.push(
        <p key={`p-${index}`} className="text-sm leading-relaxed text-slate-300 my-1">
          {parseInline(trimmed)}
        </p>
      );
    }
  });

  flushList();

  return <div className="space-y-0.5">{elements}</div>;
}
