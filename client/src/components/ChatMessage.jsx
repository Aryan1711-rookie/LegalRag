import { Children, isValidElement, cloneElement } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Scale } from "lucide-react";
import "./ChatMessage.mobile.css";

// Matches [Source 1, Page 2] and [Source 2, Pages 14–16].
const CITATION = /(\[Source\s+\d+\s*,\s*Pages?\s+\d+(?:\s*[-–—]\s*\d+)?\s*\])/gi;
const IS_CITATION = /^\[Source\s+\d+\s*,\s*Pages?\s+\d+(?:\s*[-–—]\s*\d+)?\s*\]$/i;

function CitationChip({ label }) {
  return (
    <span className="lm-citation" title={label}>
      {label.slice(1, -1).replace(/,\s*/, " · ").replace(/\s*[-–—]\s*/g, "–")}
    </span>
  );
}

function withCitations(children) {
  return Children.map(children, (child) => {
    if (typeof child === "string") {
      return child.split(CITATION).map((part, index) =>
        IS_CITATION.test(part) ? (
          <CitationChip key={index} label={part} />
        ) : (
          part
        ),
      );
    }

    // Handle citations inside markdown emphasis/links without discarding formatting.
    if (isValidElement(child) && child.props?.children) {
      return cloneElement(child, undefined, withCitations(child.props.children));
    }

    return child;
  });
}

const markdownComponents = {
  p: ({ node, children, ...props }) => <p {...props}>{withCitations(children)}</p>,
  li: ({ node, children, ...props }) => <li {...props}>{withCitations(children)}</li>,
  td: ({ node, children, ...props }) => <td {...props}>{withCitations(children)}</td>,
  th: ({ node, children, ...props }) => <th {...props}>{withCitations(children)}</th>,
  table: ({ node, ...props }) => (
    <div className="lm-table-scroll" role="region" aria-label="Scrollable legal comparison table" tabIndex={0}>
      <table {...props} />
    </div>
  ),
  a: ({ node, children, ...props }) => (
    <a {...props} target="_blank" rel="noopener noreferrer">
      {withCitations(children)}
    </a>
  ),
};

export default function ChatMessage({ role, content }) {
  if (role === "user") {
    return (
      <div className="flex min-w-0 justify-end">
        <div className="max-w-[90%] whitespace-pre-wrap break-words rounded-2xl rounded-br-md bg-[#192957] px-3.5 py-2.5 text-[14px] leading-6 text-white shadow-sm sm:max-w-[80%] sm:rounded-3xl sm:px-5 sm:py-3 sm:text-[15px] dark:bg-[#a9b8f0] dark:text-[#192957]">
          {content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-w-0 items-start gap-2.5 sm:gap-4">
      <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#192957] text-white sm:h-[30px] sm:w-[30px] dark:bg-[#a9b8f0] dark:text-[#192957]" aria-hidden="true">
        <Scale size={15} />
      </div>
      <article className="min-w-0 flex-1" aria-label="LegalMind AI response">
        <div className="lm-md">
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
            {content || ""}
          </ReactMarkdown>
        </div>
      </article>
    </div>
  );
}
