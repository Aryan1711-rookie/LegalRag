
import { useState, useEffect, useCallback } from "react";
import { NavLink, Link, useLocation } from "react-router-dom";

import {
  Search,
  Bookmark,
  Files,
  BriefcaseBusiness,
  Settings,
  FilePlus2,
  LoaderCircle,
  MessageSquare,
} from "lucide-react";

import { getSavedChats } from "../services/chat.js";

const navigation = [
  { label: "Research", path: "/research", icon: Search },
  { label: "Judgments", path: "/judgments", icon: Bookmark },
  { label: "Documents", path: "/documents", icon: Files },
  { label: "Cases", path: "/cases", icon: BriefcaseBusiness },
];

function Sidebar({ onUpload, isUploading = false }) {
  const [savedChats, setSavedChats] = useState([]);
  const [isLoadingChats, setIsLoadingChats] = useState(true);
  const [chatError, setChatError] = useState("");

  const location = useLocation();

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

  // Refresh whenever a conversation is saved or unsaved.
  useEffect(() => {
    const handleSavedChatsUpdate = () => {
      loadSavedChats();
    };

    window.addEventListener(
      "saved-chats-updated",
      handleSavedChatsUpdate
    );

    return () => {
      window.removeEventListener(
        "saved-chats-updated",
        handleSavedChatsUpdate
      );
    };
  }, [loadSavedChats]);

  return (
    <aside className="fixed bottom-0 left-0 top-[74px] z-40 flex w-[260px] flex-col border-r border-slate-200 bg-white px-3 py-5 transition-colors dark:border-slate-800 dark:bg-[#111827]">

      {/* Workspace */}
      <p className="mb-3 px-2 text-[10px] font-semibold tracking-wider text-slate-400 dark:text-slate-500">
        WORKSPACE
      </p>

      <nav className="flex flex-col gap-1">
        {navigation.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.label}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-xs transition ${
                  isActive
                    ? "bg-blue-50 font-medium text-blue-700 dark:bg-blue-500/10 dark:text-blue-400"
                    : "text-slate-600 hover:bg-slate-50 hover:text-blue-600 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-blue-400"
                }`
              }
            >
              <Icon size={17} strokeWidth={1.8} />
              {item.label}
            </NavLink>
          );
        })}
      </nav>

      {/* Upload PDF */}
      <div className="mt-4 border-t border-slate-100 pt-4 dark:border-slate-800">
        <label
          className={`flex cursor-pointer items-center justify-center gap-2 rounded-lg bg-[#192957] px-3 py-3 text-xs font-medium text-white transition hover:bg-blue-900 ${
            isUploading ? "cursor-not-allowed opacity-70" : ""
          }`}
        >
          {isUploading ? (
            <LoaderCircle size={17} className="animate-spin" />
          ) : (
            <FilePlus2 size={17} />
          )}

          {isUploading ? "Uploading..." : "Upload PDF"}

          <input
            type="file"
            accept=".pdf,application/pdf"
            className="hidden"
            disabled={isUploading}
            onChange={(e) => {
              const file = e.target.files?.[0];

              if (file && onUpload) {
                onUpload(file);
              }

              e.target.value = "";
            }}
          />
        </label>
      </div>

      {/* Saved Chats */}
      <div className="mt-6 flex min-h-0 flex-1 flex-col border-t border-slate-100 pt-5 dark:border-slate-800">
        <div className="mb-3 flex items-center justify-between px-2">
          <p className="text-[10px] font-semibold tracking-wider text-slate-400 dark:text-slate-500">
            SAVED CHATS
          </p>

          <Bookmark size={14} className="text-slate-400" />
        </div>

        <div className="flex-1 space-y-1 overflow-y-auto">
          {isLoadingChats ? (
            <div className="flex items-center gap-2 px-2 py-3 text-xs text-slate-400">
              <LoaderCircle size={14} className="animate-spin" />
              Loading saved chats...
            </div>
          ) : chatError ? (
            <p className="px-2 py-3 text-xs text-red-500">
              {chatError}
            </p>
          ) : savedChats.length === 0 ? (
            <p className="px-2 py-3 text-xs leading-5 text-slate-400 dark:text-slate-500">
              No saved conversations yet. Bookmark a research chat to find it here.
            </p>
          ) : (
            savedChats.map((chat) => (
              <NavLink
                key={chat.id}
                to={`/research/${chat.id}`}
                title={chat.title}
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-lg px-2 py-2.5 text-xs transition ${
                    isActive
                      ? "bg-blue-50 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400"
                      : "text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800"
                  }`
                }
              >
                <MessageSquare size={14} className="shrink-0" />

                <span className="min-w-0 flex-1 truncate">
                  {chat.title || "Untitled conversation"}
                </span>

                <Bookmark
                  size={12}
                  className="shrink-0 text-blue-500"
                />
              </NavLink>
            ))
          )}
        </div>
      </div>

      {/* Settings */}
      <div className="mt-4 border-t border-slate-100 pt-3 dark:border-slate-800">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-lg px-3 py-2.5 text-xs transition ${
              isActive
                ? "bg-blue-50 font-medium text-blue-700 dark:bg-blue-500/10 dark:text-blue-400"
                : "text-slate-600 hover:bg-slate-50 hover:text-blue-600 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-blue-400"
            }`
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
