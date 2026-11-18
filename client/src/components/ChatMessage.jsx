
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function ChatMessage({ role, content }) {
  const isUser = role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] rounded-2xl rounded-br-md bg-blue-600 px-4 py-3 text-sm leading-7 text-white">
          {content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <article className="w-full min-w-0 text-sm leading-7 text-slate-800 dark:text-slate-200">

        <div className="prose prose-slate max-w-none dark:prose-invert
          prose-headings:font-semibold
          prose-headings:tracking-tight
          prose-h1:text-xl
          prose-h2:mt-6 prose-h2:text-lg
          prose-h3:mt-5 prose-h3:text-base
          prose-p:my-3
          prose-strong:font-semibold
          prose-li:my-1
          prose-a:text-blue-600
          dark:prose-a:text-blue-400
          prose-blockquote:border-l-blue-500
          prose-table:text-xs
          prose-th:bg-slate-100
          dark:prose-th:bg-slate-800
          prose-td:border-slate-200
          dark:prose-td:border-slate-700
        ">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {content || ""}
          </ReactMarkdown>
        </div>

      </article>
    </div>
  );
}
