import { FileText, ChevronDown, BookOpen } from "lucide-react";

function getPageLabel(source) {
  const start = source.page_start ?? source.page;
  const end = source.page_end ?? start;
  if (start == null || start === "Unknown") return "Page unavailable";
  return String(start) === String(end) ? `Page ${start}` : `Pages ${start}–${end}`;
}

function getProvisionLabel(source) {
  const reference = source.provision_reference ??
    (source.section_number != null
      ? `${source.section_number}${source.subsection_number != null ? `(${source.subsection_number})` : ""}`
      : null);
  if (!reference) return null;
  return `${source.document_type === "bill" ? "Clause" : "Section"} ${reference}`;
}

function SourceCard({ source, index }) {
  const provision = getProvisionLabel(source);
  const title = source.document_title || source.document || "Legal document";

  return (
    <details className="group min-w-0 rounded-xl border border-[#e8e6dc] bg-white dark:border-[#3d3d3a] dark:bg-[#30302e]">
      <summary className="flex min-w-0 cursor-pointer list-none items-start gap-2.5 p-3 sm:gap-3 [&::-webkit-details-marker]:hidden">
        <FileText size={17} className="mt-0.5 shrink-0 text-[#192957] dark:text-[#a9b8f0]" aria-hidden="true" />
        <div className="min-w-0 flex-1">
          <div className="flex min-w-0 flex-wrap items-start gap-1.5 sm:gap-2">
            <span className="min-w-0 break-words text-xs font-semibold leading-5 text-[#3d3929] dark:text-[#faf9f5]">{title}</span>
            {provision && (
              <span className="max-w-full break-words rounded-md bg-[#192957]/[0.07] px-2 py-1 text-[10px] font-medium text-[#192957] dark:bg-[#a9b8f0]/10 dark:text-[#a9b8f0]">{provision}</span>
            )}
          </div>
          <p className="mt-1 text-[11px] leading-5 text-[#83827d] dark:text-[#9c9a92]">
            Source {source.source ?? index + 1} · {getPageLabel(source)}
          </p>
          {source.section_title && <p className="mt-2 break-words text-xs leading-5 text-[#6b6a68] dark:text-[#b8b6ad]">{source.section_title}</p>}
          {source.case_name && <p className="mt-2 break-words text-xs italic leading-5 text-[#6b6a68] dark:text-[#b8b6ad]">{source.case_name}</p>}
          {source.subsection_total_parts > 1 && (
            <p className="mt-1 text-[11px] text-[#83827d] dark:text-[#9c9a92]">Part {source.subsection_part} of {source.subsection_total_parts}</p>
          )}
        </div>
        <ChevronDown size={16} className="mt-1 shrink-0 text-[#9c9a92] transition-transform group-open:rotate-180" aria-hidden="true" />
      </summary>
      <div className="min-w-0 border-t border-[#e8e6dc] p-3 sm:p-4 dark:border-[#3d3d3a]">
        <p className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-[#83827d]">Original document excerpt</p>
        <p className="whitespace-pre-wrap break-words text-xs leading-6 text-[#3d3929] dark:text-[#e8e6dc]">{source.content || "Excerpt unavailable."}</p>
        <p className="mt-3 break-all text-[10px] text-[#9c9a92]">Chunk ID: {source.chunk_id || "Unavailable"}</p>
      </div>
    </details>
  );
}

export default function MessageSources({ sources = [] }) {
  if (!Array.isArray(sources) || sources.length === 0) return null;

  return (
    <details className="group/sources min-w-0 pl-0 sm:pl-[46px]">
      <summary className="flex min-h-10 w-fit max-w-full cursor-pointer list-none items-center gap-2 rounded-lg px-2 py-2 text-xs font-medium text-[#83827d] transition hover:bg-[#f0eee6] sm:px-3 dark:text-[#b8b6ad] dark:hover:bg-[#30302e] [&::-webkit-details-marker]:hidden">
        <BookOpen size={15} className="shrink-0" aria-hidden="true" />
        {sources.length} {sources.length === 1 ? "source" : "sources"}
        <ChevronDown size={14} className="shrink-0 transition-transform group-open/sources:rotate-180" aria-hidden="true" />
      </summary>
      <div className="mt-2 max-h-[min(50dvh,420px)] min-w-0 space-y-2 overflow-y-auto overscroll-contain pr-1">
        {sources.map((source, index) => (
          <SourceCard key={`${source.chunk_id || source.source || "source"}-${index}`} source={source} index={index} />
        ))}
      </div>
    </details>
  );
}
