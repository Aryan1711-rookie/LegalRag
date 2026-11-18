
import { useState } from "react";
import {
  UserRound,
  Palette,
  SlidersHorizontal,
  ShieldCheck,
  Database,
} from "lucide-react";

const sections = [
  { id: "profile", label: "Profile", icon: UserRound },
  { id: "appearance", label: "Appearance", icon: Palette },
  { id: "research", label: "Research Preferences", icon: SlidersHorizontal },
  { id: "security", label: "Security", icon: ShieldCheck },
  { id: "data", label: "Storage & Data", icon: Database },
];

function Settings() {
  const [activeSection, setActiveSection] = useState("profile");

  const active = sections.find(
    (section) => section.id === activeSection
  );

  return (
    <div className="min-h-screen bg-slate-50 px-6 py-8 dark:bg-[#0b1120]">
      <div className="mx-auto w-full max-w-6xl">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold text-slate-900 dark:text-white">
            Settings
          </h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Manage your LegalMind workspace and preferences.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-[230px_1fr]">
          <aside className="space-y-1">
            {sections.map((section) => {
              const Icon = section.icon;
              const isActive = activeSection === section.id;

              return (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`flex w-full items-center gap-3 rounded-lg px-4 py-3 text-left text-sm transition ${
                    isActive
                      ? "bg-blue-50 font-medium text-blue-700 dark:bg-blue-500/10 dark:text-blue-400"
                      : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
                  }`}
                >
                  <Icon size={18} />
                  {section.label}
                </button>
              );
            })}
          </aside>

          <section className="min-h-[500px] rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-[#111827]">
            <div className="mb-6 border-b border-slate-100 pb-5 dark:border-slate-800">
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                {active.label}
              </h2>
            </div>

            <p className="text-sm text-slate-500 dark:text-slate-400">
              Configure your {active.label.toLowerCase()} settings here.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}

export default Settings;
