import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";

import {
  Search,
  FileText,
  Image,
  Plus,
  Trash2,
  MessageSquare,
  LoaderCircle,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  UploadCloud,
  X,
  Clock3,
} from "lucide-react";

import Header from "../components/Header.jsx";
import Sidebar from "../components/Sidebar.jsx";

import {
  getDocuments,
  uploadDocument,
  deleteDocument,
} from "../services/document.js";

import { getDocumentUrl } from "../utils/documentUrl.js";

const PAGE_SIZE = 10;

const FILTERS = [
  { label: "All", value: "" },
  { label: "Ready", value: "completed" },
  { label: "Queued", value: "queued" },
  { label: "Processing", value: "processing" },
  { label: "Failed", value: "failed" },
];

/*
  Palette
  -------
  Brand navy   #192957  (light)  /  #a9b8f0 (dark accent)
  Paper        #faf9f5  (light)  /  #262624 (dark)
  Surface      #ffffff  (light)  /  #30302e (dark)
  Border       #e8e6dc  (light)  /  #3d3d3a (dark)
  Muted text   #83827d
*/

const ACCENT_TEXT = "text-[#192957] dark:text-[#a9b8f0]";
const ACCENT_SOFT = "bg-[#192957]/[0.07] dark:bg-[#a9b8f0]/10";

// Structural spacing is inline so layout never depends on generated utilities.
const layout = {
  container: { maxWidth: 880, margin: "0 auto", padding: "48px 32px" },
  heading: {
    display: "flex",
    alignItems: "flex-end",
    justifyContent: "space-between",
    gap: 24,
    marginBottom: 36,
  },
  stats: {
    display: "flex",
    flexWrap: "wrap",
    alignItems: "center",
    columnGap: 12,
    marginTop: 12,
  },
  toolbar: {
    display: "flex",
    flexWrap: "wrap",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
    marginBottom: 16,
  },
  search: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    width: "100%",
    maxWidth: 320,
    padding: "10px 14px",
  },
  segmented: { display: "inline-flex", gap: 2, padding: 4 },
  segment: { padding: "6px 14px" },
  uploadButton: {
    display: "inline-flex",
    alignItems: "center",
    gap: 8,
    padding: "10px 18px",
    flexShrink: 0,
  },
  error: {
    display: "flex",
    alignItems: "flex-start",
    justifyContent: "space-between",
    gap: 12,
    padding: "12px 16px",
    marginBottom: 16,
  },
  row: {
    display: "flex",
    alignItems: "center",
    gap: 16,
    padding: "16px 20px",
  },
  iconBox: { padding: 10, flexShrink: 0, display: "flex" },
  actions: {
    display: "flex",
    alignItems: "center",
    justifyContent: "flex-end",
    gap: 4,
    width: 76,
    flexShrink: 0,
  },
  actionBtn: { padding: 8, display: "flex" },
  empty: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    textAlign: "center",
    padding: "80px 24px",
  },
  pagination: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginTop: 20,
  },
  pageBtn: { padding: 8, display: "flex" },
};

function StatusDot({ status }) {
  if (status === "queued") {
    return (
      <span
        className="text-xs text-blue-600 dark:text-blue-400"
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
        }}
      >
        <Clock3 size={13} />
        Queued
      </span>
    );
  }
  if (status === "processing") {
    return (
      <span
        className="text-xs text-amber-600 dark:text-amber-400"
        style={{ display: "inline-flex", alignItems: "center", gap: 6 }}
      >
        <LoaderCircle size={13} className="animate-spin" />
        Processing
      </span>
    );
  }

  if (status === "failed") {
    return (
      <span
        className="text-xs text-red-600 dark:text-red-400"
        style={{ display: "inline-flex", alignItems: "center", gap: 6 }}
      >
        <AlertCircle size={13} />
        Failed
      </span>
    );
  }

  const isReady = status === "completed";

  return (
    <span
      className="text-xs capitalize text-[#83827d]"
      style={{ display: "inline-flex", alignItems: "center", gap: 6 }}
    >
      <span
        className={`rounded-full ${isReady ? "bg-emerald-500" : "bg-slate-400"}`}
        style={{ width: 6, height: 6 }}
      />
      {isReady ? "Ready" : status || "Unknown"}
    </span>
  );
}

function Documents() {
  const [darkMode, setDarkMode] = useState(
    () => localStorage.getItem("legalmind-theme") === "dark",
  );

  const [documents, setDocuments] = useState([]);
  const [recentDocuments, setRecentDocuments] = useState([]);
  const [totalDocuments, setTotalDocuments] = useState(0);

  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    queued: 0,
    processing: 0,
  });

  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);

  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [error, setError] = useState("");

  const totalPages = Math.max(1, Math.ceil(totalDocuments / PAGE_SIZE));

  // Theme
  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
    localStorage.setItem("legalmind-theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search.trim());
      setPage(1);
    }, 350);

    return () => clearTimeout(timer);
  }, [search]);

  // Fetch paginated documents
  useEffect(() => {
    let cancelled = false;

    async function loadDocuments(showLoading = true) {
      if (showLoading) setIsLoading(true);

      try {
        const result = await getDocuments({
          limit: PAGE_SIZE,
          offset: (page - 1) * PAGE_SIZE,
          search: debouncedSearch || undefined,
          status: status || undefined,
        });

        if (cancelled) return;

        setDocuments(result.documents || []);
        setTotalDocuments(result.total_documents || 0);
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    loadDocuments();

    const interval = setInterval(() => loadDocuments(false), 5000);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [page, status, debouncedSearch]);

  // Stats + sidebar documents
  const loadOverview = useCallback(async () => {
    try {
      const [all, completed, queued, processing] = await Promise.all([
        getDocuments({
          limit: 10,
          offset: 0,
        }),

        getDocuments({
          limit: 1,
          offset: 0,
          status: "completed",
        }),

        getDocuments({
          limit: 1,
          offset: 0,
          status: "queued",
        }),

        getDocuments({
          limit: 1,
          offset: 0,
          status: "processing",
        }),
      ]);

      setRecentDocuments(all.documents || []);

      setStats({
        total: all.total_documents || 0,
        completed: completed.total_documents || 0,
        queued: queued.total_documents || 0,
        processing: processing.total_documents || 0,
      });
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    loadOverview();

    const interval = setInterval(loadOverview, 10000);

    return () => clearInterval(interval);
  }, [loadOverview]);

  // Refresh current page after mutations
  async function refreshDocuments() {
    const result = await getDocuments({
      limit: PAGE_SIZE,
      offset: (page - 1) * PAGE_SIZE,
      search: debouncedSearch || undefined,
      status: status || undefined,
    });

    const count = result.total_documents || 0;
    const lastPage = Math.max(1, Math.ceil(count / PAGE_SIZE));

    if (page > lastPage) {
      setPage(lastPage);
    } else {
      setDocuments(result.documents || []);
      setTotalDocuments(count);
    }

    await loadOverview();
  }

  // Upload
  async function handleUpload(file) {
    if (!file || isUploading) return;

    if (!/\.(pdf|png|jpe?g)$/i.test(file.name)) {
      setError("Only PDF, PNG and JPEG files are supported.");
      return;
    }

    if (file.size === 0) {
      setError("The selected file is empty.");
      return;
    }

    if (file.size > 20 * 1024 * 1024) {
      setError("File must not exceed 20 MB.");
      return;
    }

    setIsUploading(true);
    setError("");

    try {
      await uploadDocument(file);
      await refreshDocuments();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  }

  // Delete
  async function handleDelete(doc) {
    if (deletingId || ["queued", "processing"].includes(doc.status)) {
      return;
    }

    const confirmed = window.confirm(
      `Delete "${doc.title}"? This action cannot be undone.`,
    );

    if (!confirmed) return;

    setDeletingId(doc.id);
    setError("");

    try {
      await deleteDocument(doc.id);
      await refreshDocuments();
      window.dispatchEvent(new Event("saved-chats-updated"));
    } catch (err) {
      setError(err.message);
    } finally {
      setDeletingId(null);
    }
  }

  // Drag and drop
  function onDragOver(e) {
    e.preventDefault();
    if (!isDragging) setIsDragging(true);
  }

  function onDragLeave(e) {
    if (!e.currentTarget.contains(e.relatedTarget)) setIsDragging(false);
  }

  function onDrop(e) {
    e.preventDefault();
    setIsDragging(false);
    handleUpload(e.dataTransfer.files?.[0]);
  }

  const hasFilters = Boolean(debouncedSearch || status);

  return (
    <div className="min-h-screen bg-[#faf9f5] transition-colors dark:bg-[#262624]">
      <Header
        darkMode={darkMode}
        onToggleDarkMode={() => setDarkMode((prev) => !prev)}
      />

      <Sidebar
        documents={recentDocuments}
        isLoadingDocuments={false}
        onUpload={handleUpload}
        isUploading={isUploading}
      />

      <main
        className="min-h-screen"
        style={{ marginLeft: 260, paddingTop: 74, boxSizing: "border-box" }}
      >
        <div style={layout.container}>
          {/* Heading */}
          <div style={layout.heading}>
            <div style={{ minWidth: 0 }}>
              <h1 className="font-serif text-4xl tracking-tight text-[#3d3929] dark:text-[#faf9f5]">
                Documents
              </h1>

              <p className="text-sm text-[#83827d]" style={layout.stats}>
                <span>{stats.total} total</span>
                <span className="text-[#d6d4cb] dark:text-[#4a4a46]">•</span>
                <span>{stats.completed} ready</span>
                {stats.queued > 0 && (
                  <>
                    <span className="text-[#d6d4cb] dark:text-[#4a4a46]">
                      •
                    </span>

                    <span className="text-amber-600 dark:text-amber-400">
                      {stats.queued} queued
                    </span>
                  </>
                )}
                {stats.processing > 0 && (
                  <>
                    <span className="text-[#d6d4cb] dark:text-[#4a4a46]">
                      •
                    </span>
                    <span className="text-amber-600 dark:text-amber-400">
                      {stats.processing} processing
                    </span>
                  </>
                )}
              </p>
            </div>

            <label
              style={layout.uploadButton}
              className={`cursor-pointer rounded-xl border border-[#192957]/20 bg-white text-sm font-medium transition hover:border-[#192957]/40 hover:bg-[#192957]/5 dark:border-[#a9b8f0]/25 dark:bg-[#30302e] dark:hover:bg-[#a9b8f0]/10 ${ACCENT_TEXT} ${
                isUploading ? "pointer-events-none opacity-60" : ""
              }`}
            >
              {isUploading ? (
                <LoaderCircle size={16} className="animate-spin" />
              ) : (
                <Plus size={16} />
              )}

              {isUploading ? "Uploading…" : "Upload"}

              <input
                type="file"
                accept=".pdf,.png,.jpg,.jpeg"
                className="hidden"
                disabled={isUploading}
                onChange={(e) => {
                  handleUpload(e.target.files?.[0]);
                  e.target.value = "";
                }}
              />
            </label>
          </div>

          {/* Toolbar */}
          <div style={layout.toolbar}>
            <div
              style={layout.search}
              className="rounded-xl border border-[#e8e6dc] bg-white transition focus-within:border-[#192957]/40 focus-within:ring-4 focus-within:ring-[#192957]/10 dark:border-[#3d3d3a] dark:bg-[#30302e] dark:focus-within:border-[#a9b8f0]/40 dark:focus-within:ring-[#a9b8f0]/10"
            >
              <Search size={16} className="shrink-0 text-[#9c9a92]" />

              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search documents"
                className="w-full bg-transparent text-sm text-[#3d3929] outline-none placeholder:text-[#9c9a92] dark:text-white"
              />

              {search && (
                <button
                  type="button"
                  onClick={() => setSearch("")}
                  aria-label="Clear search"
                  className="text-[#9c9a92] hover:text-[#3d3929] dark:hover:text-white"
                >
                  <X size={14} />
                </button>
              )}
            </div>

            <div
              style={layout.segmented}
              className="rounded-xl bg-[#f0eee6] dark:bg-[#30302e]"
            >
              {FILTERS.map((filter) => (
                <button
                  key={filter.value}
                  type="button"
                  style={layout.segment}
                  onClick={() => {
                    setStatus(filter.value);
                    setPage(1);
                  }}
                  className={`rounded-lg text-xs font-medium transition ${
                    status === filter.value
                      ? `bg-white shadow-sm dark:bg-[#3d3d3a] ${ACCENT_TEXT}`
                      : "text-[#83827d] hover:text-[#3d3929] dark:hover:text-[#faf9f5]"
                  }`}
                >
                  {filter.label}
                </button>
              ))}
            </div>
          </div>

          {/* Error */}
          {error && (
            <div
              style={layout.error}
              className="rounded-xl bg-red-50 text-sm text-red-600 dark:bg-red-950/30 dark:text-red-400"
            >
              <span>{error}</span>
              <button
                type="button"
                onClick={() => setError("")}
                aria-label="Dismiss"
                className="shrink-0 opacity-70 hover:opacity-100"
                style={{ display: "flex", marginTop: 2 }}
              >
                <X size={14} />
              </button>
            </div>
          )}

          {/* List */}
          <div
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            className={`relative overflow-hidden rounded-2xl border bg-white transition dark:bg-[#30302e] ${
              isDragging
                ? "border-[#192957] ring-4 ring-[#192957]/10 dark:border-[#a9b8f0]"
                : "border-[#e8e6dc] dark:border-[#3d3d3a]"
            }`}
          >
            {isDragging && (
              <div
                className={`absolute inset-0 z-10 bg-white/90 backdrop-blur-sm dark:bg-[#30302e]/90 ${ACCENT_TEXT}`}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 8,
                }}
              >
                <UploadCloud size={32} />
                <p className="text-sm font-medium">Drop to upload</p>
              </div>
            )}

            {isLoading ? (
              <div
                className="text-sm text-[#83827d]"
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 8,
                  padding: "96px 0",
                }}
              >
                <LoaderCircle size={18} className="animate-spin" />
                Loading…
              </div>
            ) : documents.length === 0 ? (
              <div style={layout.empty}>
                <div
                  className={`rounded-2xl ${ACCENT_SOFT}`}
                  style={{ padding: 16, marginBottom: 20, display: "flex" }}
                >
                  <UploadCloud size={26} className={ACCENT_TEXT} />
                </div>

                <h2 className="font-serif text-xl text-[#3d3929] dark:text-[#faf9f5]">
                  {hasFilters ? "Nothing matches" : "No documents yet"}
                </h2>

                <p
                  className="text-sm text-[#83827d]"
                  style={{ marginTop: 8, maxWidth: 300 }}
                >
                  {hasFilters
                    ? "Try a different search or filter."
                    : "Drag a PDF or image here, or use the upload button to begin."}
                </p>
              </div>
            ) : (
              <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
                {documents.map((doc) => {
                  const extension = doc.file_name
                    ?.split(".")
                    .pop()
                    ?.toLowerCase();

                  const isImage = ["png", "jpg", "jpeg"].includes(extension);
                  const DocumentIcon = isImage ? Image : FileText;
                  const isCompleted = doc.status === "completed";

                  const progress =
                    doc.status === "processing" &&
                    typeof doc.progress === "number"
                      ? Math.max(0, Math.min(100, doc.progress))
                      : null;

                  const meta = [
                    extension?.toUpperCase(),
                    doc.total_pages
                      ? `${doc.total_pages} ${
                          doc.total_pages === 1 ? "page" : "pages"
                        }`
                      : null,
                    doc.created_at
                      ? new Date(doc.created_at).toLocaleDateString("en-IN", {
                          day: "numeric",
                          month: "short",
                          year: "numeric",
                        })
                      : null,
                  ].filter(Boolean);

                  return (
                    <li
                      key={doc.id}
                      className="group relative border-b border-[#f0eee6] last:border-0 dark:border-[#3d3d3a]"
                    >
                      <div
                        style={layout.row}
                        className="transition hover:bg-[#faf9f5] dark:hover:bg-[#353532]"
                      >
                        <div
                          style={layout.iconBox}
                          className={`rounded-xl ${ACCENT_SOFT}`}
                        >
                          <DocumentIcon size={18} className={ACCENT_TEXT} />
                        </div>

                        <div style={{ minWidth: 0, flex: 1 }}>
                          {isCompleted ? (
                            <Link
                              to={getDocumentUrl(doc)}
                              className="block truncate text-sm font-medium text-[#3d3929] transition hover:text-[#192957] dark:text-[#faf9f5] dark:hover:text-[#a9b8f0]"
                            >
                              {doc.title}
                            </Link>
                          ) : (
                            <p className="truncate text-sm font-medium text-[#3d3929] dark:text-[#faf9f5]">
                              {doc.title}
                            </p>
                          )}

                          <p
                            className="text-xs text-[#9c9a92]"
                            style={{ marginTop: 2 }}
                          >
                            {meta.join("  ·  ")}
                          </p>
                        </div>

                        <StatusDot status={doc.status} />

                        <div
                          style={layout.actions}
                          className="transition md:opacity-0 md:group-hover:opacity-100 md:focus-within:opacity-100"
                        >
                          {isCompleted && (
                            <Link
                              to={getDocumentUrl(doc)}
                              title="Research document"
                              style={layout.actionBtn}
                              className={`rounded-lg hover:bg-[#192957]/[0.07] dark:hover:bg-[#a9b8f0]/10 ${ACCENT_TEXT}`}
                            >
                              <MessageSquare size={16} />
                            </Link>
                          )}

                          <button
                            type="button"
                            title="Delete document"
                            style={layout.actionBtn}
                            disabled={
                              Boolean(deletingId) ||
                              ["queued", "processing"].includes(doc.status)
                            }
                            onClick={() => handleDelete(doc)}
                            className="rounded-lg text-[#9c9a92] transition hover:bg-red-50 hover:text-red-500 disabled:opacity-30 dark:hover:bg-red-950/30"
                          >
                            {deletingId === doc.id ? (
                              <LoaderCircle
                                size={16}
                                className="animate-spin"
                              />
                            ) : (
                              <Trash2 size={16} />
                            )}
                          </button>
                        </div>
                      </div>

                      {progress !== null && (
                        <div
                          className="absolute bg-[#f0eee6] dark:bg-[#3d3d3a]"
                          style={{ left: 0, right: 0, bottom: 0, height: 2 }}
                        >
                          <div
                            className="h-full bg-[#192957] transition-all dark:bg-[#a9b8f0]"
                            style={{ width: `${progress}%` }}
                          />
                        </div>
                      )}
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          {/* Footer */}
          {totalDocuments > 0 && (
            <div style={layout.pagination}>
              <p className="text-xs text-[#83827d]">
                {totalDocuments}{" "}
                {totalDocuments === 1 ? "document" : "documents"}
                {totalPages > 1 && ` · Page ${page} of ${totalPages}`}
              </p>

              {totalPages > 1 && (
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <button
                    disabled={page <= 1 || isLoading}
                    onClick={() => setPage((prev) => prev - 1)}
                    aria-label="Previous page"
                    style={layout.pageBtn}
                    className="rounded-lg border border-[#e8e6dc] text-[#83827d] transition hover:bg-white disabled:opacity-30 dark:border-[#3d3d3a] dark:hover:bg-[#30302e]"
                  >
                    <ChevronLeft size={16} />
                  </button>

                  <button
                    disabled={page >= totalPages || isLoading}
                    onClick={() => setPage((prev) => prev + 1)}
                    aria-label="Next page"
                    style={layout.pageBtn}
                    className="rounded-lg border border-[#e8e6dc] text-[#83827d] transition hover:bg-white disabled:opacity-30 dark:border-[#3d3d3a] dark:hover:bg-[#30302e]"
                  >
                    <ChevronRight size={16} />
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default Documents;
