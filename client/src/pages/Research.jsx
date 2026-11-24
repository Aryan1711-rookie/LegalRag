import { useState, useEffect, useCallback, useRef } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";

import Sidebar from "../components/Sidebar.jsx";
import Header from "../components/Header.jsx";

import { useAuth } from "../context/AuthContext.jsx";
import { getDocuments, uploadDocument } from "../services/document.js";

import {
  askQuestion,
  getSavedChats,
  updateChatSavedStatus,
  getChatMessages,
} from "../services/chat.js";

import { ArrowUp, LoaderCircle, Bookmark, BookmarkCheck, Menu, X } from "lucide-react";

import ChatMessage from "../components/ChatMessage.jsx";
import DocumentProgress from "../components/DocumentProgress.jsx";
import useDocumentProgress from "../hooks/useDocument.js";
import AttachmentButton from "../components/AttachmentButton.jsx";
import { getDocumentId, getDocumentUrl } from "../utils/documentUrl.js";
import MessageSources from "../components/MessageSources.jsx";
import { searchWebResearch } from "../services/webResearch.js";
import WebSources from "../components/WebSources";
// ------------------------------
// Research modes
// ------------------------------

const RESEARCH_MODES = [
  {
    id: "documents",
    label: "Ask Documents",
    placeholder: "Ask anything about your document…",
  },
  {
    id: "summarize",
    label: "Summarize",
    placeholder: "What would you like to summarize?",
  },
  {
    id: "judgment",
    label: "Analyze Judgment",
    placeholder: "Enter a judgment or describe what you want analyzed…",
  },
  {
    id: "compare",
    label: "Compare Judgments",
    placeholder: "Which judgments would you like to compare?",
  },
  {
    id: "web",
    label: "Web Research",
    placeholder: "Ask a legal research question…",
  },
];

const MODE_PROMPTS = {
  summarize:
    "Summarize this document comprehensively. Organize the summary into the document's purpose, key topics, important facts, major arguments, conclusions, and significant legal provisions or judgments. Preserve important details and cite relevant page numbers wherever available.",

  judgment:
    "Analyze the judgment in detail. Identify the case name, court, date, facts, legal issues, arguments from both parties, applicable legal provisions, court reasoning, ratio decidendi, obiter dicta, final ruling, and its legal significance. Cite relevant page numbers wherever available.",

  compare:
    "Compare the relevant judgments available in the selected document. Analyze their facts, legal issues, applicable provisions, judicial reasoning, ratio decidendi, final decisions, and similarities or differences. Support each comparison with page references.",
};

// ------------------------------
// AI Assistant
// ------------------------------

function AssistantPanel({
  selectedDocument,
  isLoading,
  greeting,
  onUpload,
  isUploading,
}) {
  const navigate = useNavigate();
  const { chatId: urlChatId } = useParams();

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  const [isAsking, setIsAsking] = useState(false);
  const [error, setError] = useState("");

  const [chatId, setChatId] = useState(urlChatId || null);
  const [isSaved, setIsSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const [researchMode, setResearchMode] = useState("documents");

  const documentReady = selectedDocument?.status === "completed";
  const [chatReady, setChatReady] = useState(!urlChatId);
  const mounted = useRef(false);
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  const canSubmit =
    !isAsking &&
    chatReady &&
    question.trim().length > 0 &&
    (researchMode === "web" || documentReady);

  const placeholder = RESEARCH_MODES.find(
    (mode) => mode.id === researchMode,
  )?.placeholder;

  const hasMessages = messages.length > 0 || isAsking;

  // ------------------------------
  // Load existing chat
  // ------------------------------

  useEffect(() => {
    let cancelled = false;

    async function loadChat() {
      if (!urlChatId) {
        setChatReady(true);
        setChatId(null);
        setMessages([]);
        setIsSaved(false);
        setError("");
        return;
      }
      setIsSaved(false);
      setChatReady(false);
      setError("");
      setIsAsking(false);

      if (!selectedDocument?.id) return;

      try {
        const result = await getChatMessages(urlChatId);

        if (cancelled) return;

        if (result.chat.document_id !== selectedDocument.id) {
          throw new Error(
            "This conversation does not belong to the selected document.",
          );
        }
        setChatId(result.chat.id);

        setMessages(
          (result.messages || []).map((message) => ({
            role: message.role,
            content: message.content,
            sources: message.sources,
            model: message.model,
          })),
        );
        setChatReady(true);

        setIsSaved(Boolean(result.chat.is_saved));
        try {
          const savedChats = await getSavedChats();
          if (!cancelled) {
            setIsSaved(
              (savedChats.chats || []).some((chat) => chat.id === urlChatId),
            );
          }
        } catch {
          // A bookmark-list failure should not discard loaded messages.
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
          setMessages([]);
          setChatReady(false);
        }
      }
    }

    loadChat();

    return () => {
      cancelled = true;
    };
  }, [urlChatId, selectedDocument?.id]);

  // ------------------------------
  // Auto-scroll conversation
  // ------------------------------

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, isAsking]);

  // ------------------------------
  // Submit question
  // ------------------------------

  async function submitQuestion(value) {
    const userQuestion = value.trim();

    if (
      !userQuestion ||
      !chatReady ||
      isAsking ||
      (researchMode !== "web" && !documentReady)
    ) {
      return;
    }

    setIsAsking(true);
    setError("");
    setQuestion("");

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: userQuestion,
      },
    ]);

    try {
      // ------------------------------
      // WEB RESEARCH — Tavily + Groq
      // ------------------------------
      if (researchMode === "web") {
        const result = await searchWebResearch(userQuestion);

        if (!mounted.current) return;

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: result.answer,
            mode: "web",
            sources: result.sources || [],
            model: result.model,
            verification_status: result.verification_status,
            disclaimer: result.disclaimer,
          },
        ]);

        return;
      }

      // ------------------------------
      // DOCUMENT RESEARCH — Existing RAG
      // ------------------------------
      const result = await askQuestion(
        userQuestion,
        selectedDocument.id,
        chatId,
      );

      if (!mounted.current) return;

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.answer,
          mode: "documents",
          sources: result.sources,
          model: result.model,
        },
      ]);

      if (result.chat_id) {
        setChatId(result.chat_id);

        if (!urlChatId) {
          navigate(getDocumentUrl(selectedDocument, result.chat_id), {
            replace: true,
          });
        }
      }
    } catch (err) {
      if (!mounted.current) return;

      setError(err.message || "Research request failed.");

      setMessages((prev) => prev.slice(0, -1));
      setQuestion(userQuestion);
    } finally {
      if (mounted.current) {
        setIsAsking(false);
      }
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    submitQuestion(question);
  }

  // ------------------------------
  // Research mode selection
  // ------------------------------

  function handleModeClick(modeId) {
    setResearchMode(modeId);

    const prompt = MODE_PROMPTS[modeId];

    if (!prompt) return;

    if (documentReady && chatReady) {
      submitQuestion(prompt);
    } else {
      setQuestion(prompt);
    }
  }

  // ------------------------------
  // Keyboard handling
  // ------------------------------

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submitQuestion(question);
    }
  }

  // ------------------------------
  // Save chat
  // ------------------------------

  async function handleToggleSave() {
    if (!chatId || !chatReady || isSaving) return;

    setIsSaving(true);
    setError("");

    const nextSavedStatus = !isSaved;

    try {
      const result = await updateChatSavedStatus(chatId, nextSavedStatus);

      setIsSaved(result.is_saved);

      window.dispatchEvent(new Event("saved-chats-updated"));
    } catch (err) {
      setError(err.message || "Could not update saved status.");
    } finally {
      setIsSaving(false);
    }
  }

  // ------------------------------
  // Assistant layout
  // ------------------------------

  return (
    <div className="flex h-full min-h-0 min-w-0 flex-col">
      <div
        className="mb-2 flex min-w-0 shrink-0 items-center gap-2 rounded-xl bg-[#f0eee6]/70 text-[11px] sm:text-xs text-[#6b6a68] dark:bg-[#30302e] dark:text-[#b8b6ad]"
        style={{ padding: "9px 14px" }}
      >
        {documentReady && (
          <span
            className="shrink-0 rounded-full bg-emerald-500"
            style={{ width: 6, height: 6 }}
          />
        )}
        <span className="min-w-0 flex-1 truncate">
          {researchMode === "web"
            ? "Web Research · Tavily Search"
            : isLoading
              ? "Loading documents…"
              : selectedDocument?.title ||
                "Select a document from the sidebar to begin."}
        </span>
        {selectedDocument && urlChatId && (
          <button
            type="button"
            onClick={() => navigate(getDocumentUrl(selectedDocument))}
            className="shrink-0 font-medium text-[#192957] hover:underline dark:text-[#a9b8f0]"
          >
            New chat
          </button>
        )}
      </div>
      {/* Save chat */}
      {chatId && (
        <div className="flex shrink-0 justify-end pb-1">
          <button
            type="button"
            onClick={handleToggleSave}
            disabled={isSaving || !chatReady}
            className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium transition ${
              isSaved
                ? "text-[#192957] dark:text-[#a9b8f0]"
                : "text-[#83827d] hover:bg-[#f0eee6] hover:text-[#3d3929] dark:text-[#9c9a92] dark:hover:bg-[#3a3a37] dark:hover:text-[#faf9f5]"
            }`}
          >
            {isSaved ? <BookmarkCheck size={15} /> : <Bookmark size={15} />}

            {isSaving ? "Saving…" : isSaved ? "Saved" : "Save chat"}
          </button>
        </div>
      )}

      {/* Conversation, or the greeting when the chat is empty */}
      {hasMessages ? (
        <div className="min-h-0 min-w-0 flex-1 overflow-x-hidden overflow-y-auto overscroll-contain">
          <div className="space-y-6 px-1 py-4 sm:space-y-8 sm:py-6">
            {messages.map((message, index) => (
              <div key={index} className="space-y-2">
                <ChatMessage role={message.role} content={message.content} />

                {message.role === "assistant" && (
                  <>
                    {message.mode === "web" ? (
                      <WebSources
                        sources={message.sources || []}
                        disclaimer={message.disclaimer}
                      />
                    ) : (
                      <MessageSources sources={message.sources || []} />
                    )}

                    {message.model && (
                      <p className="ml-[46px] text-[11px] text-[#9c9a92]">
                        {message.model}
                      </p>
                    )}
                  </>
                )}
              </div>
            ))}

            {/* Thinking indicator */}
            {isAsking && (
              <div className="flex items-center gap-2.5 text-sm text-[#83827d] dark:text-[#9c9a92]">
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#192957] opacity-50 dark:bg-[#a9b8f0]" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-[#192957] dark:bg-[#a9b8f0]" />
                </span>
                Thinking…
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>
      ) : (
        <div className="flex min-h-0 flex-1 items-center justify-center px-2 pb-4 sm:items-end sm:pb-8">
          <h1
            className="text-center font-serif text-[#3d3929] dark:text-[#faf9f5]"
            style={{
              fontSize: "clamp(1.75rem, 6vw, 3rem)",
              lineHeight: 1.15,
              letterSpacing: "-0.02em",
            }}
          >
            {greeting}
          </h1>
        </div>
      )}

      {/* Error */}
      {error && (
        <p className="mb-3 shrink-0 rounded-xl bg-red-50 px-4 py-3 text-xs text-red-600 dark:bg-red-950/30 dark:text-red-300">
          {error}
        </p>
      )}

      {/* Composer */}
      <form
        onSubmit={handleSubmit}
        className="shrink-0 rounded-2xl border border-[#e8e6dc] bg-white p-3 shadow-[0_2px_12px_rgba(61,57,41,0.06)] transition focus-within:border-[#192957]/40 focus-within:ring-4 focus-within:ring-[#192957]/10 dark:border-[#3d3d3a] dark:bg-[#30302e] dark:shadow-none dark:focus-within:border-[#a9b8f0]/40 dark:focus-within:ring-[#a9b8f0]/10"
      >
        <textarea
          value={question}
          id="research-question"
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          maxLength={2000}
          rows={hasMessages ? 2 : 3}
          className="w-full resize-none bg-transparent px-2 pt-1 text-base sm:text-[15px] leading-6 text-[#3d3929] outline-none placeholder:text-[#9c9a92] dark:text-[#faf9f5]"
        />

        <div className="mt-2 flex items-center justify-between gap-3">
          {/* Left side controls */}
          <div className="flex min-w-0 items-center gap-2">
            <AttachmentButton onUpload={onUpload} isUploading={isUploading} />
          </div>

          {/* Send button */}
          <button
            type="submit"
            id="research-submit"
            disabled={!canSubmit}
            aria-label="Send question"
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#192957] text-white transition hover:bg-[#223675] disabled:cursor-not-allowed disabled:bg-[#e8e6dc] disabled:text-[#b8b6ad] dark:bg-[#a9b8f0] dark:text-[#192957] dark:hover:bg-[#c4cff5] dark:disabled:bg-[#3d3d3a] dark:disabled:text-[#6b6a68]"
          >
            {isAsking ? (
              <LoaderCircle size={17} className="animate-spin" />
            ) : (
              <ArrowUp size={18} />
            )}
          </button>
        </div>
      </form>

      {/* Research modes */}
      <div
        className={`flex min-w-0 shrink-0 flex-nowrap items-center justify-start gap-2 overflow-x-auto overscroll-x-contain py-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden sm:flex-wrap sm:justify-center sm:overflow-visible sm:pt-4 ${
          hasMessages ? "pb-1" : "pb-2"
        }`}
      >
        {RESEARCH_MODES.map((mode) => (
          <button
            key={mode.id}
            type="button"
            onClick={() => handleModeClick(mode.id)}
            aria-pressed={researchMode === mode.id}
            className={`shrink-0 whitespace-nowrap rounded-full border px-3 py-2 text-xs font-medium transition ${
              researchMode === mode.id
                ? "border-[#192957]/25 bg-[#192957]/[0.07] text-[#192957] dark:border-[#a9b8f0]/30 dark:bg-[#a9b8f0]/10 dark:text-[#a9b8f0]"
                : "border-[#e8e6dc] text-[#6b6a68] hover:bg-white hover:text-[#3d3929] dark:border-[#3d3d3a] dark:text-[#b8b6ad] dark:hover:bg-[#30302e] dark:hover:text-[#faf9f5]"
            }`}
          >
            {mode.label}
          </button>
        ))}
      </div>

      {/* Breathing room under the chips on the empty screen */}
      {!hasMessages && <div className="hidden flex-[1.2] sm:block" />}
    </div>
  );
}

// ------------------------------
// Research page
// ------------------------------

function Research() {
  const { user } = useAuth();
  const { documentSlug, chatId } = useParams();
  const location = useLocation();
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  const [darkMode, setDarkMode] = useState(
    () => localStorage.getItem("legalmind-theme") === "dark",
  );

  const [documents, setDocuments] = useState([]);
  const selectedDocumentId = getDocumentId(documentSlug);
  const selectedDocument = documents.find(
    (doc) => doc.id === selectedDocumentId,
  );

  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [documentError, setDocumentError] = useState("");
  const [processingDocumentId, setProcessingDocumentId] = useState(null);

  const { document: processingDocument, error: processingError } =
    useDocumentProgress(processingDocumentId);

  const loadDocuments = useCallback(async () => {
    setIsLoading(true);
    setDocumentError("");

    try {
      const loaded = [];
      const limit = 100;
      let offset = 0;
      while (true) {
        const result = await getDocuments({ limit, offset });
        const batch = result.documents || [];
        loaded.push(...batch);
        offset += batch.length;
        if (batch.length < limit || offset >= result.total_documents) break;
      }

      setDocuments(loaded);
    } catch (error) {
      setDocumentError(error.message);
    } finally {
      setIsLoading(false);
    }
  }, []);
  useEffect(() => {
    if (!processingDocument) return;

    if (processingDocument.status === "completed") {
      loadDocuments();
    }

    if (processingDocument.status === "failed") {
      loadDocuments();
    }
  }, [processingDocument, loadDocuments]);

  // Close the drawer when navigating and allow Escape to dismiss it.
  useEffect(() => {
    setMobileSidebarOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    if (!mobileSidebarOpen) return;

    function onKeyDown(event) {
      if (event.key === "Escape") setMobileSidebarOpen(false);
    }

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [mobileSidebarOpen]);

  // Theme
  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);

    localStorage.setItem("legalmind-theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  // Load documents
  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  // Upload document
  async function handleUpload(file) {
    if (!file) return;

    const allowedExtensions = [".pdf", ".png", ".jpg", ".jpeg"];

    const fileName = file.name.toLowerCase();

    if (!allowedExtensions.some((ext) => fileName.endsWith(ext))) {
      setDocumentError("Only PDF, PNG and JPEG files are supported.");
      return;
    }

    if (file.size === 0) {
      setDocumentError("The selected file is empty.");
      return;
    }

    if (file.size > 20 * 1024 * 1024) {
      setDocumentError("File must not exceed 20 MB.");
      return;
    }

    setIsUploading(true);
    setDocumentError("");

    try {
      const result = await uploadDocument(file);

      setProcessingDocumentId(result.document_id);

      await loadDocuments();
    } catch (error) {
      setDocumentError(error.message);
    } finally {
      setIsUploading(false);
    }
  }

  // Greeting
  const firstName = user?.full_name?.trim()?.split(/\s+/)[0] || "there";

  const hour = new Date().getHours();

  const greeting = `${
    hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening"
  }, ${firstName}`;

  const sidebarProps = {
    onUpload: handleUpload,
    isUploading,
    documents,
    isLoadingDocuments: isLoading,
  };

  return (
    <div className="h-[100dvh] overflow-hidden bg-[#faf9f5] transition-colors dark:bg-[#262624]">
      <Header
        darkMode={darkMode}
        onToggleDarkMode={() => setDarkMode((prev) => !prev)}
      />

      {/* Preserve the existing desktop sidebar. */}
      <div className="hidden lg:block">
        <Sidebar {...sidebarProps} />
      </div>

      {/* Mobile drawer. The transformed wrapper also contains fixed-position
          sidebar styles used by the existing desktop Sidebar component. */}
      {mobileSidebarOpen && (
        <div className="fixed inset-0 z-[100] lg:hidden">
          <button
            type="button"
            aria-label="Close navigation"
            className="absolute inset-0 bg-black/45 backdrop-blur-[2px]"
            onClick={() => setMobileSidebarOpen(false)}
          />
          <div
            id="mobile-research-navigation"
            role="dialog"
            aria-modal="true"
            aria-label="Research navigation"
            className="absolute inset-y-0 left-0 w-[min(85vw,300px)] overflow-hidden bg-[#faf9f5] shadow-2xl [transform:translateZ(0)] dark:bg-[#262624]"
            onClickCapture={(event) => {
              if (event.target.closest("a[href]")) {
                setMobileSidebarOpen(false);
              }
            }}
          >
            <button
              type="button"
              onClick={() => setMobileSidebarOpen(false)}
              aria-label="Close sidebar"
              className="absolute right-3 top-3 z-[110] flex h-10 w-10 items-center justify-center rounded-lg bg-[#f0eee6] text-[#3d3929] dark:bg-[#383835] dark:text-white"
            >
              <X size={20} />
            </button>
            <Sidebar
              {...sidebarProps}
              mobile
              onNavigate={() => setMobileSidebarOpen(false)}
            />
          </div>
        </div>
      )}

      <main className="h-full min-w-0 overflow-hidden pt-[74px] lg:ml-[260px]">
        <div className="mx-auto flex h-full w-full max-w-5xl min-w-0 flex-col px-3 pb-[max(12px,env(safe-area-inset-bottom))] pt-2 sm:px-5 lg:px-6 lg:pb-5 lg:pt-4">
          <div className="mb-2 flex shrink-0 items-center gap-2 lg:hidden">
            <button
              type="button"
              aria-label="Open navigation"
              aria-expanded={mobileSidebarOpen}
              aria-controls="mobile-research-navigation"
              onClick={() => setMobileSidebarOpen(true)}
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-[#e8e6dc] text-[#3d3929] dark:border-[#454540] dark:text-[#faf9f5]"
            >
              <Menu size={20} />
            </button>
            <span className="truncate text-sm font-medium text-[#3d3929] dark:text-[#faf9f5]">
              Research workspace
            </span>
          </div>

          {documentError && (
            <p className="mb-3 shrink-0 text-center text-xs text-red-500" role="alert">
              {documentError}
            </p>
          )}

          {processingDocument && (
            <div className="shrink-0">
              <DocumentProgress document={processingDocument} />
            </div>
          )}

          {processingError && (
            <p className="mb-3 shrink-0 text-center text-xs text-red-500" role="alert">
              {processingError}
            </p>
          )}

          <div className="min-h-0 min-w-0 flex-1">
            <AssistantPanel
              key={`${selectedDocumentId || "home"}:${chatId || "new"}`}
              selectedDocument={selectedDocument}
              isLoading={isLoading}
              greeting={greeting}
              onUpload={handleUpload}
              isUploading={isUploading}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default Research;
