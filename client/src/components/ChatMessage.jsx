import { Children } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Scale } from "lucide-react";

/*
  Palette
  Navy  #192957 (light) / #a9b8f0 (dark)
  Ink   #3d3929 (light) / #e8e6dc (dark)
  Sand  #f0eee6 (light) / #30302e (dark)

  Spacing for rendered markdown lives in plain CSS below, so it never
  depends on generated utility classes or the typography plugin.
*/

const MARKDOWN_CSS = `
.lm-md { font-size: 15px; line-height: 1.8; color: #3d3929; overflow-wrap: anywhere; }
.lm-md > *:first-child { margin-top: 0 !important; }
.lm-md > *:last-child { margin-bottom: 0 !important; }

.lm-md p { margin: 0 0 16px; }

.lm-md h1, .lm-md h2, .lm-md h3, .lm-md h4 {
  font-family: ui-serif, Georgia, Cambria, "Times New Roman", serif;
  font-weight: 600;
  letter-spacing: -0.01em;
  line-height: 1.3;
  color: #3d3929;
  margin: 32px 0 12px;
}
.lm-md h1 { font-size: 24px; }
.lm-md h2 { font-size: 20px; }
.lm-md h3 { font-size: 17px; margin: 26px 0 10px; }
.lm-md h4 { font-size: 15px; margin: 22px 0 8px; }

.lm-md ul, .lm-md ol { margin: 0 0 16px; padding-left: 24px; }
.lm-md ul { list-style: disc; }
.lm-md ol { list-style: decimal; }
.lm-md li { margin: 6px 0; padding-left: 4px; }
.lm-md li > p { margin: 0; }
.lm-md li > ul, .lm-md li > ol { margin: 6px 0 0; }
.lm-md li::marker { color: #9c9a92; }

.lm-md strong { font-weight: 600; color: #192957; }
.lm-md em { font-style: italic; }

.lm-md a {
  color: #192957;
  font-weight: 500;
  text-decoration: underline;
  text-decoration-color: rgba(25, 41, 87, 0.3);
  text-underline-offset: 4px;
}
.lm-md a:hover { text-decoration-color: #192957; }

.lm-md blockquote {
  margin: 20px 0;
  padding: 8px 18px;
  border-left: 3px solid #192957;
  background: rgba(240, 238, 230, 0.6);
  border-radius: 0 12px 12px 0;
  color: #6b6a68;
}
.lm-md blockquote > p:last-child { margin-bottom: 0; }

.lm-md hr { margin: 28px 0; border: 0; border-top: 1px solid #e8e6dc; }

.lm-md table { width: 100%; border-collapse: collapse; font-size: 13px; margin: 0; }
.lm-md th, .lm-md td { padding: 12px 16px; text-align: left; vertical-align: top; border-bottom: 1px solid #f0eee6; }
.lm-md th { background: #f0eee6; font-weight: 600; }
.lm-md tr:last-child td { border-bottom: 0; }

.lm-md pre {
  margin: 20px 0;
  padding: 16px 18px;
  border-radius: 12px;
  background: #f0eee6;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.6;
}
.lm-md code { background: #f0eee6; padding: 2px 6px; border-radius: 6px; font-size: 0.9em; }
.lm-md pre code { background: transparent; padding: 0; }

/* Dark mode */
.dark .lm-md { color: #e8e6dc; }
.dark .lm-md h1, .dark .lm-md h2, .dark .lm-md h3, .dark .lm-md h4 { color: #faf9f5; }
.dark .lm-md strong { color: #a9b8f0; }
.dark .lm-md a { color: #a9b8f0; text-decoration-color: rgba(169, 184, 240, 0.35); }
.dark .lm-md a:hover { text-decoration-color: #a9b8f0; }
.dark .lm-md blockquote { border-left-color: #a9b8f0; background: #30302e; color: #b8b6ad; }
.dark .lm-md hr { border-top-color: #3d3d3a; }
.dark .lm-md th { background: #30302e; }
.dark .lm-md th, .dark .lm-md td { border-bottom-color: #3d3d3a; }
.dark .lm-md pre, .dark .lm-md code { background: #30302e; }
.dark .lm-md pre code { background: transparent; }
.dark .lm-md li::marker { color: #6b6a68; }
`;

// Turns "[Source 1, Page 2]" into a small citation chip.
const CITATION =
  /(\[Source\s+\d+,\s*Pages?\s+\d+(?:\s*[-–—]\s*\d+)?\])/gi;

function CitationChip({ label }) {
  return (
    <span
      className="whitespace-nowrap rounded-md bg-[#192957]/[0.07] text-[11px] font-medium text-[#192957] dark:bg-[#a9b8f0]/10 dark:text-[#a9b8f0]"
      style={{
        display: "inline-block",
        padding: "1px 7px",
        margin: "0 2px",
        lineHeight: 1.6,
        verticalAlign: "baseline",
      }}
    >
      {label}
    </span>
  );
}

function withCitations(children) {
  return Children.map(children, (child) => {
    if (typeof child !== "string") return child;

    return child.split(CITATION).map((part, index) => {
      if (/^\[Source\s+\d+/i.test(part)) {
        const label = part
          .slice(1, -1)
          .replace(/,\s*/g, " · ")
          .replace(/(\d+)\s*[-–—]\s*(\d+)/g, "$1–$2");

        return (
          <CitationChip
            key={index}
            label={label}
          />
        );
      }

      return part;
    });
  });
}

const components = {
  p: ({ node, children, ...props }) => (
    <p {...props}>{withCitations(children)}</p>
  ),
  li: ({ node, children, ...props }) => (
    <li {...props}>{withCitations(children)}</li>
  ),
  td: ({ node, children, ...props }) => (
    <td {...props}>{withCitations(children)}</td>
  ),
  th: ({ node, children, ...props }) => (
    <th {...props}>{withCitations(children)}</th>
  ),
  table: ({ node, ...props }) => (
    <div
      className="overflow-x-auto rounded-xl border border-[#e8e6dc] dark:border-[#3d3d3a]"
      style={{ margin: "24px 0" }}
    >
      <table {...props} />
    </div>
  ),
};

export default function ChatMessage({ role, content }) {
  const isUser = role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div
          className="whitespace-pre-wrap break-words rounded-3xl rounded-br-lg bg-[#192957] text-[15px] text-white shadow-sm dark:bg-[#a9b8f0] dark:text-[#192957]"
          style={{
            maxWidth: "80%",
            padding: "12px 20px",
            lineHeight: 1.7,
          }}
        >
          {content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start" style={{ gap: 16 }}>
      <style>{MARKDOWN_CSS}</style>

      {/* Assistant mark */}
      <div
        className="rounded-full bg-[#192957] text-white dark:bg-[#a9b8f0] dark:text-[#192957]"
        style={{
          width: 30,
          height: 30,
          flexShrink: 0,
          marginTop: 2,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Scale size={15} />
      </div>

      <article style={{ minWidth: 0, flex: 1 }}>
        <div className="lm-md">
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
            {content || ""}
          </ReactMarkdown>
        </div>
      </article>
    </div>
  );
}