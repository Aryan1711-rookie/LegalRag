
import { ExternalLink, AlertTriangle, Globe2, ShieldAlert } from "lucide-react";

const DEFAULT_DISCLAIMER =
  "Web Research is AI-generated and has not undergone claim-level legal verification. Verify important conclusions against official legal sources.";

function getSafeUrl(value) {
  if (typeof value !== "string") return null;

  try {
    const url = new URL(value);

    if (!["http:", "https:"].includes(url.protocol)) {
      return null;
    }

    return url;
  } catch {
    return null;
  }
}

function WebSourceCard({ source, index }) {
  const parsedUrl = getSafeUrl(source?.url);

  if (!parsedUrl) return null;

  const hostname = parsedUrl.hostname.replace(/^www\./, "");
  const sourceNumber = source.source_id ?? index + 1;

  return (
    <a
      href={parsedUrl.href}
      target="_blank"
      rel="noopener noreferrer"
      aria-label={`Open source ${sourceNumber}: ${source.title || hostname}`}
      className="
        group flex min-w-0 items-start gap-3
        rounded-xl border border-[#e8e6dc]
        bg-white p-3.5
        transition-all duration-200
        hover:border-[#192957]/25
        hover:bg-[#faf9f5]
        hover:shadow-sm
        focus-visible:outline-2
        focus-visible:outline-offset-2
        focus-visible:outline-[#192957]
        active:scale-[0.99]

        sm:gap-4 sm:p-4

        dark:border-[#3d3d3a]
        dark:bg-[#30302e]
        dark:hover:border-[#a9b8f0]/30
        dark:hover:bg-[#363633]
        dark:focus-visible:outline-[#a9b8f0]
      "
    >
      {/* Source identification */}
      <div
        className="
          flex h-9 w-9 shrink-0 items-center justify-center
          rounded-lg bg-[#192957]/[0.07]
          text-[#192957]

          sm:h-10 sm:w-10

          dark:bg-[#a9b8f0]/10
          dark:text-[#a9b8f0]
        "
      >
        <Globe2 size={18} strokeWidth={1.7} />
      </div>

      {/* Source details */}
      <div className="min-w-0 flex-1">
        <div className="mb-1.5 flex min-w-0 items-center gap-2">
          <span
            className="
              shrink-0 rounded-md bg-[#f0eee6]
              px-2 py-0.5 font-mono text-[10px]
              font-semibold text-[#6b6a68]

              dark:bg-[#3d3d3a]
              dark:text-[#b8b6ad]
            "
          >
            SOURCE {sourceNumber}
          </span>
        </div>

        <p
          className="
            line-clamp-2 break-words
            text-[13px] font-semibold leading-5
            text-[#3d3929]

            sm:text-sm sm:leading-6

            dark:text-[#faf9f5]
          "
        >
          {source.title || "Web source"}
        </p>

        <p
          className="
            mt-1.5 truncate text-[11px]
            text-[#83827d]

            sm:text-xs

            dark:text-[#9c9a92]
          "
          title={hostname}
        >
          {hostname}
        </p>
      </div>

      <ExternalLink
        size={16}
        aria-hidden="true"
        className="
          mt-1 shrink-0 text-[#9c9a92]
          transition-colors duration-200
          group-hover:text-[#192957]
          dark:group-hover:text-[#a9b8f0]
        "
      />
    </a>
  );
}

export default function WebSources({
  sources = [],
  disclaimer,
}) {
  const safeSources = Array.isArray(sources)
    ? sources.filter((source) => getSafeUrl(source?.url))
    : [];

  return (
    <div
      className="
        ml-0 mt-4 min-w-0 space-y-4
        sm:ml-[46px] sm:mt-5
      "
    >
      {safeSources.length > 0 && (
        <section aria-label="Web research sources">
          {/* Section header */}
          <div className="mb-3 flex items-center gap-2">
            <Globe2
              size={15}
              className="shrink-0 text-[#192957] dark:text-[#a9b8f0]"
            />

            <h3 className="text-xs font-semibold text-[#3d3929] sm:text-sm dark:text-[#faf9f5]">
              Web Sources
            </h3>

            <span
              className="
                rounded-full bg-[#f0eee6]
                px-2 py-0.5 text-[10px]
                font-semibold text-[#6b6a68]

                dark:bg-[#3d3d3a]
                dark:text-[#b8b6ad]
              "
            >
              {safeSources.length}
            </span>
          </div>

          {/* Responsive source list */}
          <div className="grid min-w-0 grid-cols-1 gap-2.5 xl:grid-cols-2">
            {safeSources.map((source, index) => (
              <WebSourceCard
                key={`${source.source_id ?? "source"}-${index}`}
                source={source}
                index={index}
              />
            ))}
          </div>
        </section>
      )}

      {/* Verification notice */}
      <div
        role="note"
        className="
          flex min-w-0 items-start gap-3
          rounded-xl border border-amber-200/80
          bg-amber-50/80 p-3.5

          sm:p-4

          dark:border-amber-900/50
          dark:bg-amber-950/20
        "
      >
        <ShieldAlert
          size={17}
          className="mt-0.5 shrink-0 text-amber-700 dark:text-amber-400"
        />

        <div className="min-w-0">
          <p className="mb-1 text-xs font-semibold text-amber-900 dark:text-amber-200">
            Research verification notice
          </p>

          <p className="break-words text-xs leading-5 text-amber-900/80 dark:text-amber-200/80 sm:leading-6">
            {disclaimer || DEFAULT_DISCLAIMER}
          </p>
        </div>
      </div>
    </div>
  );
}
