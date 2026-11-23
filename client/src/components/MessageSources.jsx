import { FileText, ChevronDown, BookOpen } from "lucide-react";

function getPageLabel(source) {
  const start = source.page_start ?? source.page;
  const end = source.page_end ?? start;

  if (start == null || start === "Unknown") {
    return "Page unavailable";
  }

  if (String(start) === String(end)) {
    return `Page ${start}`;
  }

  return `Pages ${start}–${end}`;
}

function getProvisionLabel(source) {
  const reference =
    source.provision_reference ??
    (source.section_number != null
      ? `${source.section_number}${
          source.subsection_number != null
            ? `(${source.subsection_number})`
            : ""
        }`
      : null);

  if (!reference) return null;

  const label =
    source.document_type === "bill" ? "Clause" : "Section";

  return `${label} ${reference}`;
}

function SourceCard({ source }) {
  const provision = getProvisionLabel(source);

  return (
    <details className="group rounded-xl border border-[#e8e6dc] bg-white dark:border-[#3d3d3a] dark:bg-[#30302e]">
      <summary className="flex cursor-pointer list-none items-start gap-3 p-3 [&::-webkit-details-marker]:hidden">

        <FileText
          size={17}
          className="mt-1 shrink-0 text-[#192957] dark:text-[#a9b8f0]"
        />

        <div className="min-w-0 flex-1">

          <div className="flex flex-wrap items-center gap-2">
            <span className="break-words text-xs font-semibold text-[#3d3929] dark:text-[#faf9f5]">
              {source.document_title ||
                source.document ||
                "Legal document"}
            </span>

            {provision && (
              <span className="rounded-md bg-[#192957]/[0.07] px-2 py-1 text-[10px] font-medium text-[#192957] dark:bg-[#a9b8f0]/10 dark:text-[#a9b8f0]">
                {provision}
              </span>
            )}
          </div>

          <p className="mt-1 text-[11px] text-[#83827d] dark:text-[#9c9a92]">
            Source {source.source} · {getPageLabel(source)}
          </p>

          {source.section_title && (
            <p className="mt-2 text-xs leading-5 text-[#6b6a68] dark:text-[#b8b6ad]">
              {source.section_title}
            </p>
          )}

          {source.case_name && (
            <p className="mt-2 text-xs italic text-[#6b6a68] dark:text-[#b8b6ad]">
              {source.case_name}
            </p>
          )}

          {source.subsection_total_parts > 1 && (
            <p className="mt-1 text-[11px] text-[#83827d]">
              Part {source.subsection_part} of{" "}
              {source.subsection_total_parts}
            </p>
          )}

        </div>

        <ChevronDown
          size={15}
          className="mt-1 shrink-0 text-[#9c9a92] transition-transform group-open:rotate-180"
        />

      </summary>

      <div className="border-t border-[#e8e6dc] p-4 dark:border-[#3d3d3a]">

        <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-[#83827d]">
          Original document excerpt
        </p>

        <p className="whitespace-pre-wrap break-words text-xs leading-6 text-[#3d3929] dark:text-[#e8e6dc]">
          {source.content || "Excerpt unavailable."}
        </p>

        <p className="mt-3 text-[10px] text-[#9c9a92]">
          Chunk ID: {source.chunk_id || "Unavailable"}
        </p>

      </div>
    </details>
  );
}

export default function MessageSources({ sources = [] }) {
  if (!Array.isArray(sources) || sources.length === 0) {
    return null;
  }

  return (
    <details className="group/sources ml-[46px]">

      <summary className="flex w-fit cursor-pointer list-none items-center gap-2 rounded-lg px-3 py-2 text-xs font-medium text-[#83827d] transition hover:bg-[#f0eee6] dark:text-[#b8b6ad] dark:hover:bg-[#30302e] [&::-webkit-details-marker]:hidden">

        <BookOpen size={14} />

        {sources.length}{" "}
        {sources.length === 1 ? "source" : "sources"}

        <ChevronDown
          size={13}
          className="transition-transform group-open/sources:rotate-180"
        />

      </summary>

      <div className="mt-2 max-h-[420px] space-y-2 overflow-y-auto pr-1">
        {sources.map((source, index) => (
          <SourceCard
            key={`${source.chunk_id || source.source}-${index}`}
            source={source}
          />
        ))}
      </div>

    </details>
  );
}