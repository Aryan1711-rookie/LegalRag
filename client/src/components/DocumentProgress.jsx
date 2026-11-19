import {
  FileText,
  CheckCircle2,
  Circle,
  LoaderCircle,
  AlertCircle,
} from "lucide-react";

const STAGES = [
  { id: "uploaded", label: "PDF uploaded" },
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
  const progress = completed ? 100 : document.progress ?? 0;

  const currentIndex = STAGES.findIndex(
    (stage) => stage.id === document.processing_stage
  );

  const currentLabel = completed
    ? "Document ready for research"
    : failed
      ? "Document processing failed"
      : STAGES[currentIndex]?.label || "Processing document";

  return (
    <div className="mb-4 shrink-0 rounded-xl border border-[#deddd5] bg-white p-4 dark:border-[#454541] dark:bg-[#30302e]">

      {/* Header */}
      <div className="flex items-center gap-3">
        <FileText className="h-7 w-7 shrink-0 text-[#77766e]" />

        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-semibold text-[#30302e] dark:text-[#efeee8]">
            {document.file_name}
          </p>

          <p className="text-xs text-gray-500">
            {document.total_pages} pages
          </p>
        </div>

        <span
          className={`rounded-full px-2.5 py-1 text-xs font-medium ${
            completed
              ? "bg-green-100 text-green-700"
              : failed
                ? "bg-red-100 text-red-700"
                : "bg-amber-100 text-amber-700"
          }`}
        >
          {completed
            ? "Completed"
            : failed
              ? "Failed"
              : "Processing"}
        </span>
      </div>

      {/* Progress bar */}
      <div
        role="progressbar"
        aria-label="Document processing"
        aria-valuenow={progress}
        aria-valuemin={0}
        aria-valuemax={100}
        className="mt-4 h-2 overflow-hidden rounded-full bg-gray-200 dark:bg-[#454541]"
      >
        <div
          className={`h-full rounded-full transition-all duration-700 ${
            failed
              ? "bg-red-500"
              : completed
                ? "bg-green-500"
                : "bg-blue-500"
          }`}
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="mt-2 flex justify-between text-xs text-gray-500">
        <span>{currentLabel}</span>
        <span>{progress}%</span>
      </div>

      {/* Processing stages */}
      {!completed && !failed && (
        <div className="mt-4 grid grid-cols-2 gap-3">
          {STAGES.map((stage, index) => {
            const done = index < currentIndex;
            const active = index === currentIndex;

            return (
              <div
                key={stage.id}
                className={`flex items-center gap-2 text-xs ${
                  done
                    ? "text-green-600"
                    : active
                      ? "text-blue-500"
                      : "text-gray-400"
                }`}
              >
                {done ? (
                  <CheckCircle2 size={15} />
                ) : active ? (
                  <LoaderCircle
                    size={15}
                    className="animate-spin"
                  />
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
        <div className="mt-3 flex items-center gap-2 text-xs text-red-500">
          <AlertCircle size={16} />
          {document.error_message || "Ingestion failed."}
        </div>
      )}

      {completed && (
        <div className="mt-3 flex items-center gap-2 text-xs text-green-600">
          <CheckCircle2 size={16} />
          You can now ask questions about this document.
        </div>
      )}
    </div>
  );
}