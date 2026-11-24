import { useState, useEffect, useCallback } from "react";
import { NavLink, useLocation } from "react-router-dom";

import {
  Search,
  Bookmark,
  Files,
  BriefcaseBusiness,
  Settings,
  FilePlus2,
  FileText,
  Image,
  LoaderCircle,
  MessageSquare,
  ChevronDown,
  ChevronRight,
  AlertCircle,
  ArrowRight,
} from "lucide-react";

import { getSavedChats } from "../services/chat.js";
import { getDocumentUrl, getDocumentId } from "../utils/documentUrl.js";

const navigation = [
  { label: "Research", path: "/research", icon: Search },
  { label: "Judgments", path: "/judgments", icon: Bookmark },
  { label: "Documents", icon: Files },
  { label: "Cases", path: "/cases", icon: BriefcaseBusiness },
];

/*
  Palette
  Navy accent  #192957  (light)  /  #a9b8f0 (dark)
  Border       #e8e6dc  (light)  /  #3d3d3a (dark)
  Paper        #faf9f5  (light)  /  #30302e (dark hover)
*/

const ITEM_ACTIVE =
  "bg-[#192957]/[0.07] font-medium text-[#192957] dark:bg-[#a9b8f0]/10 dark:text-[#a9b8f0]";

const ITEM_IDLE =
  "text-[#6b6a68] hover:bg-[#faf9f5] hover:text-[#3d3929] dark:text-[#b8b6ad] dark:hover:bg-[#30302e] dark:hover:text-[#faf9f5]";

const NAV_ITEM =
  "flex items-center gap-3 rounded-xl px-3 py-2.5 text-[13px] transition";

const SUB_ITEM =
  "flex items-center gap-2 rounded-lg px-2 py-2.5 text-xs transition";

const SECTION_LABEL =
  "text-[10px] font-semibold uppercase tracking-[0.14em] text-[#9c9a92]";

const DIVIDER = "border-[#f0eee6] dark:border-[#3d3d3a]";

function Sidebar({
  onUpload,
  isUploading = false,
  documents = [],
  isLoadingDocuments = false,
  mobile = false,
  onNavigate,
}) {
  const [savedChats, setSavedChats] = useState([]);
  const [isLoadingChats, setIsLoadingChats] = useState(true);
  const [chatError, setChatError] = useState("");
  const [documentsOpen, setDocumentsOpen] = useState(true);

  const location = useLocation();

  // Let the parent close the mobile drawer after navigation.
  const handleNavigation = () => onNavigate?.();

  const currentSlug = location.pathname.split("/")[2];

  const activeDocumentId = getDocumentId(
    currentSlug ? decodeURIComponent(currentSlug) : null,
  );

  const loadSavedChats = useCallback(async () => {
    setIsLoadingChats(true);
    setChatError("");

    try {
      const result = await getSavedChats();
      setSavedChats(result.chats || []);
    } catch (error) {
      setChatError(error.message);
    } finally {
      setIsLoadingChats(false);
    }
  }, []);

  useEffect(() => {
    loadSavedChats();
  }, [loadSavedChats, location.pathname]);

  useEffect(() => {
    const handleUpdate = () => loadSavedChats();

    window.addEventListener("saved-chats-updated", handleUpdate);

    return () => {
      window.removeEventListener("saved-chats-updated", handleUpdate);
    };
  }, [loadSavedChats]);

  function getChatUrl(chat) {
    const document = documents.find((doc) => doc.id === chat.document_id);

    if (document) {
      return getDocumentUrl(document, chat.id);
    }

    if (chat.document_id) {
      return getDocumentUrl(
        {
          id: chat.document_id,
          title: "Document",
        },
        chat.id,
      );
    }

    return null;
  }

  return (
    <aside
      aria-label="Research sidebar"
      className={`${mobile
        ? "absolute inset-0 w-full pt-16"
        : "fixed bottom-0 left-0 top-[74px] z-40 w-[260px] pt-5"
      } flex min-h-0 flex-col overflow-hidden border-r border-[#e8e6dc] bg-white px-3 pb-[max(16px,env(safe-area-inset-bottom))] transition-colors dark:border-[#3d3d3a] dark:bg-[#262624]`}
    >
      {/* Workspace */}

      <p className={`mb-3 px-3 ${SECTION_LABEL}`}>Workspace</p>

      <nav className="flex flex-col gap-1">
        {navigation.map((item) => {
          const Icon = item.icon;

          if (item.label === "Documents") {
            return (
              <div key={item.label}>
                <button
                  type="button"
                  aria-expanded={documentsOpen}
                  onClick={() => setDocumentsOpen((prev) => !prev)}
                  className={`${NAV_ITEM} w-full ${ITEM_IDLE}`}
                >
                  <Files size={17} strokeWidth={1.8} />

                  <span className="flex-1 text-left">Documents</span>

                  <span className="text-[11px] text-[#9c9a92]">
                    {documents.length}
                  </span>

                  {documentsOpen ? (
                    <ChevronDown size={14} className="text-[#9c9a92]" />
                  ) : (
                    <ChevronRight size={14} className="text-[#9c9a92]" />
                  )}
                </button>

                {/* Document List */}

                {documentsOpen && (
                  <div className="ml-5 mt-1 max-h-56 space-y-0.5 overflow-y-auto border-l border-[#e8e6dc] pl-2 dark:border-[#3d3d3a]">
                    {isLoadingDocuments ? (
                      <div className="flex items-center gap-2 px-2 py-3 text-xs text-[#9c9a92]">
                        <LoaderCircle size={13} className="animate-spin" />
                        Loading documents…
                      </div>
                    ) : documents.length === 0 ? (
                      <p className="px-2 py-3 text-xs text-[#9c9a92]">
                        No documents uploaded.
                      </p>
                    ) : (
                      documents.slice(0, 3).map((doc) => {
                        const extension = doc.file_name
                          ?.split(".")
                          .pop()
                          ?.toLowerCase();

                        const isImage = ["png", "jpg", "jpeg"].includes(
                          extension,
                        );

                        const DocumentIcon = isImage ? Image : FileText;

                        const isReady = doc.status === "completed";

                        const isActive = activeDocumentId === doc.id;

                        if (!isReady) {
                          return (
                            <div
                              key={doc.id}
                              className="flex items-center gap-2 rounded-lg px-2 py-2 text-xs text-[#9c9a92]"
                            >
                              {doc.status === "failed" ? (
                                <AlertCircle
                                  size={14}
                                  className="shrink-0 text-red-500"
                                />
                              ) : (
                                <LoaderCircle
                                  size={14}
                                  className="shrink-0 animate-spin"
                                />
                              )}

                              <span className="truncate">{doc.title}</span>
                            </div>
                          );
                        }

                        return (
                          <NavLink
                            key={doc.id}
                            to={getDocumentUrl(doc)}
                            onClick={handleNavigation}
                            title={doc.title}
                            className={`${SUB_ITEM} ${
                              isActive ? ITEM_ACTIVE : ITEM_IDLE
                            }`}
                          >
                            <DocumentIcon size={14} className="shrink-0" />

                            <span className="truncate">{doc.title}</span>
                          </NavLink>
                        );
                      })
                    )}

                    <NavLink
                      to="/documents"
                      onClick={handleNavigation}
                      className="mt-2 flex items-center justify-between rounded-lg px-2 py-2 text-xs font-medium text-[#192957] transition hover:bg-[#192957]/[0.05] dark:text-[#a9b8f0] dark:hover:bg-[#a9b8f0]/10"
                    >
                      <span>View all documents</span>
                      <ArrowRight size={14} />
                    </NavLink>
                  </div>
                )}
              </div>
            );
          }

          return (
            <NavLink
              key={item.label}
              to={item.path}
              onClick={handleNavigation}
              end
              className={({ isActive }) =>
                `${NAV_ITEM} ${isActive ? ITEM_ACTIVE : ITEM_IDLE}`
              }
            >
              <Icon size={17} strokeWidth={1.8} />
              {item.label}
            </NavLink>
          );
        })}
      </nav>

      {/* Upload Document */}

      <div className={`mt-4 border-t pt-4 ${DIVIDER}`}>
        <label
          className={`flex cursor-pointer items-center justify-center gap-2 rounded-xl bg-[#192957] px-3 py-3 text-[13px] font-medium text-white transition hover:bg-[#223675] dark:bg-[#a9b8f0] dark:text-[#192957] dark:hover:bg-[#c4cff5] ${
            isUploading ? "cursor-not-allowed opacity-70" : ""
          }`}
        >
          {isUploading ? (
            <LoaderCircle size={17} className="animate-spin" />
          ) : (
            <FilePlus2 size={17} />
          )}

          {isUploading ? "Uploading…" : "Upload Document"}

          <input
            type="file"
            accept=".pdf,.png,.jpg,.jpeg"
            className="hidden"
            disabled={isUploading}
            onChange={(e) => {
              const file = e.target.files?.[0];

              if (file && onUpload) {
                onUpload(file);
                if (mobile) handleNavigation();
              }

              e.target.value = "";
            }}
          />
        </label>
      </div>

      {/* Saved Chats */}

      <div className={`mt-6 flex min-h-0 flex-1 flex-col border-t pt-5 ${DIVIDER}`}>
        <div className="mb-3 flex items-center justify-between px-3">
          <p className={SECTION_LABEL}>Saved chats</p>

          <Bookmark size={14} className="text-[#9c9a92]" />
        </div>

        <div className="flex-1 space-y-0.5 overflow-y-auto">
          {isLoadingChats ? (
            <div className="flex items-center gap-2 px-3 py-3 text-xs text-[#9c9a92]">
              <LoaderCircle size={14} className="animate-spin" />
              Loading saved chats…
            </div>
          ) : chatError ? (
            <p className="px-3 py-3 text-xs text-red-500">{chatError}</p>
          ) : savedChats.length === 0 ? (
            <p className="px-3 py-3 text-xs leading-5 text-[#9c9a92]">
              No saved conversations yet.
            </p>
          ) : (
            savedChats.map((chat) => {
              const chatUrl = getChatUrl(chat);

              if (!chatUrl) {
                return (
                  <p
                    key={chat.id}
                    className="px-3 py-2 text-xs text-[#9c9a92]"
                  >
                    {chat.title || "Untitled conversation"}
                  </p>
                );
              }

              return (
                <NavLink
                  key={chat.id}
                  to={chatUrl}
                  onClick={handleNavigation}
                  title={chat.title}
                  end
                  className={({ isActive }) =>
                    `${SUB_ITEM} px-3 ${isActive ? ITEM_ACTIVE : ITEM_IDLE}`
                  }
                >
                  <MessageSquare size={14} className="shrink-0" />

                  <span className="min-w-0 flex-1 truncate">
                    {chat.title || "Untitled conversation"}
                  </span>

                  <Bookmark
                    size={12}
                    className="shrink-0 text-[#192957] dark:text-[#a9b8f0]"
                  />
                </NavLink>
              );
            })
          )}
        </div>
      </div>

      {/* Settings */}

      <div className={`mt-4 border-t pt-3 ${DIVIDER}`}>
        <NavLink
          to="/settings"
          onClick={handleNavigation}
          className={({ isActive }) =>
            `${NAV_ITEM} ${isActive ? ITEM_ACTIVE : ITEM_IDLE}`
          }
        >
          <Settings size={17} strokeWidth={1.8} />
          Settings
        </NavLink>
      </div>
    </aside>
  );
}

export default Sidebar;