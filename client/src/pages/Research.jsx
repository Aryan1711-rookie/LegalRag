import { useState, useEffect, useCallback, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";

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

import { ArrowUp, LoaderCircle, Bookmark, BookmarkCheck } from "lucide-react";

import ChatMessage from "../components/ChatMessage.jsx";

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

// Warm, calm styling shared by the small selects
const pillSelect =
  "max-w-full cursor-pointer rounded-lg border border-transparent bg-transparent px-2.5 py-1.5 text-xs font-medium text-[#6b6a68] outline-none transition hover:bg-[#f0eee6] focus:bg-[#f0eee6] dark:text-[#b8b6ad] dark:hover:bg-[#3a3a37] dark:focus:bg-[#3a3a37]";

// ------------------------------
// AI Assistant
// ------------------------------

function AssistantPanel({
  documents,
  selectedDocument,
  setSelectedDocument,
  isLoading,
  greeting,
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

  const readyDocuments = documents.filter((doc) => doc.status === "completed");

  const canSubmit =
    !isAsking && question.trim().length > 0 && !!selectedDocument;

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
        setChatId(null);
        setMessages([]);
        setIsSaved(false);
        setError("");
        return;
      }
      setIsSaved(false);
      setError("");
      setIsAsking(false);

      try {
        const result = await getChatMessages(urlChatId);

        if (cancelled) return;

        setChatId(result.chat.id);
        setSelectedDocument(result.chat.document_id || "");

        setMessages(
          (result.messages || []).map((message) => ({
            role: message.role,
            content: message.content,
          })),
        );

        const savedChats = await getSavedChats();

        if (!cancelled) {
          setIsSaved(savedChats.chats.some((chat) => chat.id === urlChatId));
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
          setMessages([]);
        }
      }
    }

    loadChat();

    return () => {
      cancelled = true;
    };
  }, [urlChatId, setSelectedDocument]);

  
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

    if (!userQuestion || !selectedDocument || isAsking) return;

    setIsAsking(true);
    setError("");
    setQuestion("");

    setMessages((prev) => [...prev, { role: "user", content: userQuestion }]);

    try {
      const result = await askQuestion(userQuestion, selectedDocument, chatId);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.answer,
          sources: result.sources,
          model: result.model,
        },
      ]);

      if (result.chat_id) {
        setChatId(result.chat_id);

        if (!urlChatId) {
          navigate(`/research/${result.chat_id}`, {
            replace: true,
          });
        }
      }
    } catch (err) {
      setError(err.message);

      setMessages((prev) => prev.slice(0, -1));
      setQuestion(userQuestion);
    } finally {
      setIsAsking(false);
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

    if (selectedDocument) {
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
  // Document selection
  // ------------------------------

  function handleDocumentChange(e) {
    setSelectedDocument(e.target.value);
    setChatId(null);
    setMessages([]);
    setQuestion("");
    setIsSaved(false);
    setError("");

    navigate("/research", { replace: true });
  }

  // ------------------------------
  // Save chat
  // ------------------------------

  async function handleToggleSave() {
  if (!chatId || isSaving) return;

  setIsSaving(true);
  setError("");

  const nextSavedStatus = !isSaved;

  try {
    const result = await updateChatSavedStatus(
      chatId,
      nextSavedStatus
    );

    setIsSaved(result.is_saved);

    window.dispatchEvent(new Event("saved-chats-updated"));
  } catch (err) {
    setError(err.message || "Could not update saved status.");
  } finally {
    setIsSaving(false);
  }
}

  // ------------------------------
  // Empty document state
  // ------------------------------

  if (!isLoading && readyDocuments.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center text-center">
        <h1 className="font-serif text-3xl text-[#3d3929] dark:text-[#faf9f5]">
          {greeting}
        </h1>

        <p className="mt-3 text-sm text-[#6b6a68] dark:text-[#b8b6ad]">
          Upload a PDF from the sidebar to start your research.
        </p>
      </div>
    );
  }

  // ------------------------------
  // Assistant layout
  // ------------------------------

  return (
    <div className="flex h-full min-h-0 flex-col">
      {/* Save chat */}
      {chatId && (
        <div className="flex shrink-0 justify-end pb-1">
          <button
            type="button"
            onClick={handleToggleSave}
            disabled={isSaving}
            className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium transition ${
              isSaved
                ? "text-[#c96442] dark:text-[#d97757]"
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
        <div className="min-h-0 flex-1 overflow-y-auto">
          <div className="space-y-8 py-6">
            {messages.map((message, index) => (
              <div key={index} className="space-y-2">
                <ChatMessage role={message.role} content={message.content} />

                {message.role === "assistant" &&
                  (message.sources?.length > 0 || message.model) && (
                    <p className="ml-1 text-[11px] text-[#9c9a92]">
                      {[
                        message.sources?.length > 0 &&
                          `${message.sources.length} ${
                            message.sources.length === 1
                              ? "source"
                              : "sources"
                          }`,
                        message.model,
                      ]
                        .filter(Boolean)
                        .join(" · ")}
                    </p>
                  )}
              </div>
            ))}

            {/* Thinking indicator */}
            {isAsking && (
              <div className="flex items-center gap-2.5 text-sm text-[#83827d] dark:text-[#9c9a92]">
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#c96442] opacity-60" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-[#c96442]" />
                </span>
                Thinking…
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>
      ) : (
        <div className="flex flex-1 items-end justify-center pb-8">
          <h1 className="text-center font-serif text-3xl text-[#3d3929] dark:text-[#faf9f5] sm:text-4xl">
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
        className="shrink-0 rounded-2xl border border-[#e8e6dc] bg-white p-3 shadow-[0_2px_12px_rgba(61,57,41,0.06)] transition focus-within:border-[#d9d6c8] focus-within:shadow-[0_4px_20px_rgba(61,57,41,0.1)] dark:border-[#3d3d3a] dark:bg-[#30302e] dark:shadow-none dark:focus-within:border-[#52524e]"
      >
        <textarea
          value={question}
          id="research-question"
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          maxLength={2000}
          rows={hasMessages ? 2 : 3}
          className="w-full resize-none bg-transparent px-2 pt-1 text-[15px] leading-6 text-[#3d3929] outline-none placeholder:text-[#9c9a92] dark:text-[#faf9f5]"
        />

        <div className="mt-2 flex items-center justify-between gap-3">
          <select
            value={selectedDocument}
            onChange={handleDocumentChange}
            aria-label="Select a document"
            className={`${pillSelect} max-w-[220px] truncate`}
          >
            <option value="">Choose document</option>

            {readyDocuments.map((doc) => (
              <option key={doc.id} value={doc.id}>
                {doc.title}
              </option>
            ))}
          </select>

          <button
            type="submit"
            id="research-submit"
            disabled={!canSubmit}
            aria-label="Send question"
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#c96442] text-white transition hover:bg-[#b5573a] disabled:cursor-not-allowed disabled:bg-[#e8e6dc] disabled:text-[#b8b6ad] dark:disabled:bg-[#3d3d3a] dark:disabled:text-[#6b6a68]"
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
        className={`flex shrink-0 flex-wrap items-center justify-center gap-2 pt-4 ${
          hasMessages ? "pb-1" : "pb-2"
        }`}
      >
        {RESEARCH_MODES.map((mode) => (
          <button
            key={mode.id}
            type="button"
            onClick={() => handleModeClick(mode.id)}
            aria-pressed={researchMode === mode.id}
            className={`rounded-full border px-3 py-1.5 text-xs font-medium transition ${
              researchMode === mode.id
                ? "border-[#c96442]/30 bg-[#c96442]/10 text-[#b5573a] dark:border-[#d97757]/30 dark:bg-[#d97757]/10 dark:text-[#d97757]"
                : "border-[#e8e6dc] text-[#6b6a68] hover:bg-white hover:text-[#3d3929] dark:border-[#3d3d3a] dark:text-[#b8b6ad] dark:hover:bg-[#30302e] dark:hover:text-[#faf9f5]"
            }`}
          >
            {mode.label}
          </button>
        ))}
      </div>

      {/* Breathing room under the chips on the empty screen */}
      {!hasMessages && <div className="flex-[1.2]" />}
    </div>
  );
}

// ------------------------------
// Research page
// ------------------------------

function Research() {
  const { user } = useAuth();

  const [darkMode, setDarkMode] = useState(
    () => localStorage.getItem("legalmind-theme") === "dark",
  );

  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState("");

  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [documentError, setDocumentError] = useState("");

  // Reset URL to /research on a full page load.
  useEffect(() => {
    window.history.replaceState(null, "", "/research");
  }, []);

  const loadDocuments = useCallback(async () => {
    setIsLoading(true);
    setDocumentError("");

    try {
      const result = await getDocuments({
        limit: 20,
        offset: 0,
      });

      const loaded = result.documents || [];

      setDocuments(loaded);

      setSelectedDocument((current) => {
        const stillExists = loaded.some(
          (doc) => doc.id === current && doc.status === "completed",
        );

        if (stillExists) return current;

        return loaded.find((doc) => doc.status === "completed")?.id || "";
      });
    } catch (error) {
      setDocumentError(error.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

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
    if (file.size > 20 * 1024 * 1024) {
      setDocumentError("PDF file must be smaller than 20 MB.");
      return;
    }

    if (
      file.type !== "application/pdf" &&
      !file.name.toLowerCase().endsWith(".pdf")
    ) {
      setDocumentError("Only PDF files are supported.");
      return;
    }

    setIsUploading(true);
    setDocumentError("");

    try {
      await uploadDocument(file);
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

  return (
    <div className="h-screen overflow-hidden bg-[#faf9f5] transition-colors dark:bg-[#262624]">
      <Header
        darkMode={darkMode}
        onToggleDarkMode={() => setDarkMode((prev) => !prev)}
      />

      <Sidebar onUpload={handleUpload} isUploading={isUploading} />

      <main className="ml-[260px] h-screen overflow-hidden pt-[74px]">
        <div className="mx-auto flex h-full w-full max-w-3xl flex-col px-6 pb-5 pt-4">
          {/* Document error */}
          {documentError && (
            <p className="mb-3 shrink-0 text-center text-xs text-red-500">
              {documentError}
            </p>
          )}

          {/* Assistant fills remaining height */}
          <div className="min-h-0 flex-1">
            <AssistantPanel
              documents={documents}
              selectedDocument={selectedDocument}
              setSelectedDocument={setSelectedDocument}
              isLoading={isLoading}
              greeting={greeting}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default Research;