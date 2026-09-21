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
          className="px-1.5 py-0.5 mx-0.5 text-xs font-mono bg-white/10 text-white rounded"
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
 * ChatGPT-style typography markdown renderer.
 */
export default function MarkdownRenderer({ content }) {
  if (!content) return null;

  const lines = content.split('\n');
  const elements = [];
  let currentList = [];

  const flushList = () => {
    if (currentList.length > 0) {
      elements.push(
        <ul key={`list-${elements.length}`} className="my-2 space-y-1 text-slate-200">
          {currentList.map((item, idx) => (
            <li key={idx} className="flex items-start gap-2 text-[15px] leading-relaxed">
              <span className="text-slate-400 select-none">•</span>
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
        <hr key={`hr-${index}`} className="my-3 border-t border-white/10" />
      );
      return;
    }

    // Headings: ### Heading 3
    if (trimmed.startsWith('### ')) {
      flushList();
      elements.push(
        <h3
          key={`h3-${index}`}
          className="text-sm font-semibold text-white uppercase tracking-wider mt-4 mb-1.5"
        >
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
          className="text-base font-semibold text-white mt-4 mb-2"
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
        <h1 key={`h1-${index}`} className="text-lg font-bold text-white mt-4 mb-2">
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
        <div key={`num-${index}`} className="flex items-start gap-2 my-1 text-[15px] leading-relaxed text-slate-200">
          <span className="text-sm font-medium text-slate-400 min-w-[18px]">
            {numMatch[1]}.
          </span>
          <div>{parseInline(numMatch[2])}</div>
        </div>
      );
      return;
    }

    // Normal text or empty line
    flushList();
    if (trimmed === '') {
      elements.push(<div key={`empty-${index}`} className="h-1.5" />);
    } else {
      elements.push(
        <p key={`p-${index}`} className="text-[15px] leading-relaxed text-slate-200 my-1">
          {parseInline(trimmed)}
        </p>
      );
    }
  });

  flushList();

  return <div className="space-y-0.5">{elements}</div>;
}
