import {
  FileText,
  CheckCircle2,
  Circle,
  LoaderCircle,
  AlertCircle,
  Clock3,
} from "lucide-react";

const STAGES = [
  { id: "uploaded", label: "PDF uploaded" },
  { id: "queued", label: "Waiting for worker" },
  { id: "parsing", label: "Extracting text" },
  { id: "normalizing", label: "Normalizing text" },
  { id: "chunking", label: "Creating chunks" },
  { id: "embedding", label: "Generating embeddings" },
  { id: "indexing", label: "Indexing document" },
];

export default function DocumentProgress({ document }) {
  if (!document) return null;

  const completed = document.status === "completed";
  const failed = document.status === "failed";
  const queued = document.status === "queued";

  const progress = completed
    ? 100
    : Math.max(0, Math.min(100, document.progress ?? 0));

  const currentIndex = STAGES.findIndex(
    (stage) => stage.id === (queued ? "queued" : document.processing_stage),
  );

  const currentLabel = completed
    ? "Document ready for research"
    : failed
      ? "Document processing failed"
      : queued
        ? "Waiting for an available worker"
        : STAGES[currentIndex]?.label || "Processing document";

  const statusText = completed
    ? "Completed"
    : failed
      ? "Failed"
      : queued
        ? "Queued"
        : "Processing";

  const statusColor = completed
    ? "text-emerald-600 dark:text-emerald-400"
    : failed
      ? "text-red-600 dark:text-red-400"
      : queued
        ? "text-amber-600 dark:text-amber-400"
        : "text-blue-600 dark:text-blue-400";

  const barColor = failed
    ? "bg-red-500"
    : completed
      ? "bg-emerald-500"
      : queued
        ? "bg-amber-400"
        : "bg-[#192957] dark:bg-[#a9b8f0]";
  return (
    <div
      className="shrink-0 rounded-2xl border border-[#e8e6dc] bg-white dark:border-[#3d3d3a] dark:bg-[#30302e]"
      style={{ padding: "18px 20px", marginBottom: 16 }}
    >
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <div
          className="rounded-xl bg-[#192957]/[0.07] dark:bg-[#a9b8f0]/10"
          style={{ padding: 10, display: "flex", flexShrink: 0 }}
        >
          <FileText size={18} className="text-[#192957] dark:text-[#a9b8f0]" />
        </div>

        <div style={{ minWidth: 0, flex: 1 }}>
          <p className="truncate text-sm font-medium text-[#3d3929] dark:text-[#faf9f5]">
            {document.file_name}
          </p>

          {document.total_pages ? (
            <p className="text-xs text-[#9c9a92]" style={{ marginTop: 2 }}>
              {document.total_pages}{" "}
              {document.total_pages === 1 ? "page" : "pages"}
            </p>
          ) : null}
        </div>

        <span
          className={`text-xs font-medium ${statusColor}`}
          style={{ display: "inline-flex", alignItems: "center", gap: 6 }}
        >
          <span
            className="rounded-full bg-current"
            style={{ width: 6, height: 6 }}
          />
          {statusText}
        </span>
      </div>

      {/* Progress bar */}
      <div
        role="progressbar"
        aria-label="Document processing"
        aria-valuenow={progress}
        aria-valuemin={0}
        aria-valuemax={100}
        className="overflow-hidden rounded-full bg-[#f0eee6] dark:bg-[#3d3d3a]"
        style={{ height: 4, marginTop: 18 }}
      >
        <div
          className={`h-full rounded-full transition-all duration-700 ${barColor}`}
          style={{ width: `${progress}%` }}
        />
      </div>

      <div
        className="text-xs text-[#83827d] dark:text-[#b8b6ad]"
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginTop: 10,
        }}
      >
        <span>{currentLabel}</span>
        <span>{progress}%</span>
      </div>
      {queued && (
        <div
          className="rounded-xl bg-amber-50 text-xs
      text-amber-700 dark:bg-amber-500/10
      dark:text-amber-400"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: "12px",
            marginTop: 14,
          }}
        >
          <Clock3 size={16} className="shrink-0" />
          Your document is safely uploaded and will automatically start
          processing when a worker becomes available.
        </div>
      )}

      {/* Processing stages */}
      {!completed && !failed && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: "10px 16px",
            marginTop: 18,
          }}
        >
          {STAGES.map((stage, index) => {
            const done = index < currentIndex;
            const active = index === currentIndex;

            return (
              <div
                key={stage.id}
                className={`text-xs ${
                  done
                    ? "text-emerald-600 dark:text-emerald-400"
                    : active
                      ? "font-medium text-[#192957] dark:text-[#a9b8f0]"
                      : "text-[#b8b6ad] dark:text-[#6b6a68]"
                }`}
                style={{ display: "flex", alignItems: "center", gap: 8 }}
              >
                {done ? (
                  <CheckCircle2 size={15} />
                ) : active ? (
                  queued ? (
                    <Clock3 size={15} />
                  ) : (
                    <LoaderCircle size={15} className="animate-spin" />
                  )
                ) : (
                  <Circle size={15} />
                )}

                {stage.label}
              </div>
            );
          })}
        </div>
      )}

      {failed && (
        <div
          className="text-xs text-red-600 dark:text-red-400"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            marginTop: 14,
          }}
        >
          <AlertCircle size={16} />
          {document.error_message || "Ingestion failed."}
        </div>
      )}

      {completed && (
        <div
          className="text-xs text-emerald-600 dark:text-emerald-400"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            marginTop: 14,
          }}
        >
          <CheckCircle2 size={16} />
          You can now ask questions about this document.
        </div>
      )}
    </div>
  );
}
