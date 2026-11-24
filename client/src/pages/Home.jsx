import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../services/apiFetch.js";
import {
  ArrowRight,
  ArrowUpRight,
  ScanText,
  Languages,
  Files,
  BookOpenCheck,
  ShieldCheck,
  Search,
  FileText,
  Quote,
} from "lucide-react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";

import Header from "../components/Header.jsx";
import Preloader from "../components/Preloader.jsx";
const API_BASE_URL = "";

const FEATURES = [
  {
    icon: Files,
    title: "Document Intelligence",
    description:
      "Upload judgments, affidavits, scanned PDFs and legal document images.",
  },
  {
    icon: ScanText,
    title: "Intelligent OCR",
    description:
      "Extract Hindi and English text from scanned documents using Surya OCR.",
  },
  {
    icon: Languages,
    title: "Multilingual Research",
    description:
      "Research documents seamlessly in Hindi, English and Hinglish.",
  },
  {
    icon: BookOpenCheck,
    title: "Source-Backed Answers",
    description:
      "Explore your documents with answers grounded in retrieved passages and page references.",
  },
  {
    icon: Search,
    title: "Semantic Search",
    description:
      "Find relevant legal information beyond simple keyword matching.",
  },
  {
    icon: ShieldCheck,
    title: "Grounded Intelligence",
    description:
      "Designed to reduce hallucinations and identify questions unsupported by your documents.",
  },
];

const STEPS = [
  {
    number: "01",
    title: "Upload",
    description: "Add a legal PDF or scanned image.",
  },
  {
    number: "02",
    title: "Understand",
    description: "LegalMind extracts and indexes your document.",
  },
  {
    number: "03",
    title: "Research",
    description: "Ask questions and explore source-backed answers.",
  },
];

const TECHNOLOGIES = [
  "Retrieval-Augmented Generation",
  "Surya OCR",
  "Multilingual E5",
  "FastAPI",
  "PostgreSQL",
  "pgvector",
];

const LANGUAGES = ["हिन्दी", "English", "Hinglish"];

/*
  Palette
  Ink (navy)  #192957
  Ink deep    #0f1a3d
  Paper       #faf9f5
  Sand        #f0eee6
  Rule        #e8e6dc
  Body        #3d3929
  Muted       #6b6a68
*/

// Structural layout is inline so it never depends on generated utilities.
const layout = {
  column: { maxWidth: 1180, margin: "0 auto", padding: "0 32px" },
  hero: { padding: "96px 0 72px" },
  actions: {
    display: "flex",
    flexWrap: "wrap",
    alignItems: "center",
    gap: 28,
    marginTop: 48,
  },
  section: { padding: "112px 0" },
  mockGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
  },
  featureRow: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
    alignItems: "center",
    gap: "16px 48px",
    padding: "36px 0",
  },
  stepsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
    gap: 20,
  },
  statsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
    gap: 0,
  },
};

const bigHeading = {
  fontSize: "clamp(2.25rem, 5.5vw, 4rem)",
  lineHeight: 1.06,
  letterSpacing: "-0.03em",
};

// Backend readiness check
function useBackendStatus() {
  const [status, setStatus] = useState("starting");

  useEffect(() => {
    let cancelled = false;
    let timer;
    let controller;

    async function checkHealth() {
      controller = new AbortController();

      const timeout = setTimeout(() => controller.abort(), 5000);

      try {
        const response = await apiFetch(`${API_BASE_URL}/health/ready`, {
          signal: controller.signal,
          cache: "no-store",
          headers: {
    "ngrok-skip-browser-warning": "true",
  },
        });

        if (!response.ok) {
          throw new Error("Backend starting");
        }

        const data = await response.json();

        if (!["healthy", "ready"].includes(data.status)) {
          throw new Error("Backend not ready");
        }

        if (!cancelled) {
          setStatus("ready");
        }
      } catch {
        if (!cancelled) {
          setStatus("starting");
          timer = setTimeout(checkHealth, 8000);
        }
      } finally {
        clearTimeout(timeout);
      }
    }

    checkHealth();

    return () => {
      cancelled = true;
      clearTimeout(timer);
      controller?.abort();
    };
  }, []);

  return status;
}

function SectionLabel({ children, light = false }) {
  return (
    <p
      className={`text-xs font-medium uppercase ${
        light ? "text-white/60" : "text-[#83827d]"
      }`}
      style={{ letterSpacing: "0.14em", marginBottom: 24 }}
    >
      {children}
    </p>
  );
}

// Product preview shown in the hero: a document, a question, a grounded answer.
function ResearchPreview() {
  return (
    <div
      className="lm-home-preview overflow-hidden text-white"
      style={{
        ...layout.mockGrid,
        background: "linear-gradient(160deg, #192957 0%, #0f1a3d 100%)",
        borderRadius: 28,
        boxShadow: "0 40px 80px -40px rgba(25,41,87,0.55)",
      }}
      aria-hidden="true"
    >
      {/* Documents */}
      <div
        className="lm-home-preview-documents"
        style={{
          padding: 32,
          borderRight: "1px solid rgba(255,255,255,0.1)",
        }}
      >
        <p
          className="text-xs uppercase text-white/50"
          style={{ letterSpacing: "0.14em", marginBottom: 20 }}
        >
          Your documents
        </p>

        {[
          { name: "Judgment_2023.pdf", meta: "42 pages · English", on: true },
          { name: "Affidavit_scan.jpg", meta: "OCR · हिन्दी", on: false },
          { name: "Petition_draft.pdf", meta: "18 pages · Hinglish", on: false },
        ].map((doc) => (
          <div
            key={doc.name}
            style={{
              display: "flex",
              gap: 12,
              alignItems: "flex-start",
              padding: "14px 16px",
              borderRadius: 14,
              marginBottom: 8,
              background: doc.on ? "rgba(255,255,255,0.1)" : "transparent",
            }}
          >
            <FileText size={16} className="text-white/70" style={{ marginTop: 2 }} />
            <div>
              <p className="text-sm">{doc.name}</p>
              <p className="text-xs text-white/50" style={{ marginTop: 2 }}>
                {doc.meta}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Conversation */}
      <div className="lm-home-preview-answer" style={{ padding: 32, gridColumn: "span 1" }}>
        <div
          className="lm-home-preview-question text-sm"
          style={{
            background: "rgba(255,255,255,0.1)",
            borderRadius: 16,
            padding: "14px 18px",
            maxWidth: 360,
            marginLeft: "auto",
          }}
        >
          What did the court hold on the delay in filing?
        </div>

        <div style={{ marginTop: 20 }}>
          <p className="text-[15px] text-white/90" style={{ lineHeight: 1.7 }}>
            The court condoned the delay, finding the applicant showed
            sufficient cause for the period in question.
          </p>

          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 16 }}>
            {["Page 14", "Page 17"].map((page) => (
              <span
                key={page}
                className="text-xs"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 6,
                  padding: "6px 12px",
                  borderRadius: 999,
                  background: "rgba(255,255,255,0.12)",
                }}
              >
                <Quote size={11} />
                {page}
              </span>
            ))}
          </div>
        </div>

        <div
          className="text-xs text-white/60"
          style={{
            marginTop: 28,
            paddingTop: 20,
            borderTop: "1px solid rgba(255,255,255,0.1)",
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <ShieldCheck size={14} />
          Unsupported questions are flagged, not guessed.
        </div>
      </div>
    </div>
  );
}

function Home() {
  const backendStatus = useBackendStatus();
  const reduceMotion = useReducedMotion();
  const [showPreloader, setShowPreloader] = useState(
    () => !sessionStorage.getItem("legalmind-intro-seen"),
  );
  const [activeFeature, setActiveFeature] = useState(null);

  useEffect(() => {
    if (!showPreloader) return;

    const timer = setTimeout(() => {
      setShowPreloader(false);

      sessionStorage.setItem("legalmind-intro-seen", "true");
    }, 3000);

    return () => clearTimeout(timer);
  }, [showPreloader]);

  const isReady = backendStatus === "ready";

  const fadeUp = {
    hidden: {
      opacity: 0,
      y: reduceMotion ? 0 : 24,
    },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.7,
        ease: [0.22, 1, 0.36, 1],
      },
    },
  };

  const stagger = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: reduceMotion ? 0 : 0.1,
      },
    },
  };

  const reveal = {
    variants: fadeUp,
    initial: "hidden",
    whileInView: "visible",
    viewport: { once: true, amount: 0.25 },
  };

  return (
    <div className="lm-home min-h-screen overflow-x-clip bg-[#faf9f5] text-[#3d3929]">
      <style>{`
        @keyframes lm-marquee {
          from { transform: translateX(0); }
          to { transform: translateX(-50%); }
        }
        .lm-marquee-track {
          display: flex;
          width: max-content;
          animation: lm-marquee 38s linear infinite;
        }
        .lm-marquee:hover .lm-marquee-track { animation-play-state: paused; }
        @media (prefers-reduced-motion: reduce) {
          .lm-marquee-track { animation: none; }
        }

        /* Responsive-only overrides. Desktop inline layout remains intact. */
        .lm-home { width: 100%; }
        .lm-home-column { width: 100%; box-sizing: border-box; }
        .lm-home-preview, .lm-home-preview > div { min-width: 0; }
        .lm-home-preview { grid-template-columns: repeat(2, minmax(0, 1fr)) !important; }
        .lm-home-preview p { overflow-wrap: anywhere; }
        .lm-home-preview-documents, .lm-home-preview-answer { min-width: 0; }
        @media (max-width: 1023px) {
          .lm-home-column { padding-left: 24px !important; padding-right: 24px !important; }
          .lm-home-hero { padding-top: 76px !important; padding-bottom: 58px !important; }
          .lm-home-section { padding-top: 80px !important; padding-bottom: 80px !important; }
          .lm-home-feature-row { grid-template-columns: minmax(0, 1fr) !important; gap: 16px !important; }
          .lm-home-steps { grid-template-columns: repeat(2, minmax(0, 1fr)) !important; }
          .lm-home-preview-documents, .lm-home-preview-answer { padding: 24px !important; }
          .lm-home-footer { padding-top: 28px !important; padding-bottom: 28px !important; }
        }
        @media (max-width: 639px) {
          .lm-home-column { padding-left: 16px !important; padding-right: 16px !important; }
          .lm-home-hero { padding-top: 54px !important; padding-bottom: 40px !important; }
          .lm-home-hero-title { font-size: clamp(2.55rem, 10.5vw, 4.25rem) !important; line-height: 1.04 !important; margin-top: 28px !important; overflow-wrap: anywhere; }
          .lm-home-lead { font-size: 1rem !important; line-height: 1.7 !important; }
          .lm-home-section { padding-top: 60px !important; padding-bottom: 60px !important; }
          .lm-home-preview { grid-template-columns: minmax(0, 1fr) !important; border-radius: 18px !important; }
          .lm-home-preview-documents { border-right: 0 !important; border-bottom: 1px solid rgba(255,255,255,0.1); }
          .lm-home-preview-documents, .lm-home-preview-answer { padding: 20px !important; }
          .lm-home-preview-question { margin-left: 0 !important; }
          .lm-home-steps { grid-template-columns: minmax(0, 1fr) !important; margin-top: 36px !important; }
          .lm-home-steps > div { min-height: 215px !important; padding: 24px !important; }
          .lm-home-feature-row { padding-top: 24px !important; padding-bottom: 24px !important; }
          .lm-home-marquee { margin-top: 56px !important; padding-top: 20px !important; padding-bottom: 20px !important; }
          .lm-home-footer { align-items: flex-start !important; padding-top: 24px !important; padding-bottom: 24px !important; }
          .lm-home-primary-cta { padding: 14px 22px !important; }
          .lm-home-secondary-cta { display: inline-flex; align-items: center; min-height: 44px; }
        }
      `}</style>

      <AnimatePresence>{showPreloader && <Preloader />}</AnimatePresence>

      {/* Navigation */}

      <Header />

      {/* Spacer for the fixed header */}
      <div style={{ height: 74 }} />

      {/* Hero */}

      <section className="lm-home-column" style={layout.column}>
        <motion.div
          variants={stagger}
          initial="hidden"
          animate="visible"
          className="lm-home-hero"
          style={layout.hero}
        >
          <motion.div variants={fadeUp}>
            <div
              role="status"
              className="text-xs text-[#6b6a68]"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                padding: "8px 14px",
                borderRadius: 999,
                border: "1px solid #e8e6dc",
                background: "#fff",
              }}
            >
              <span
                className={`rounded-full ${
                  isReady ? "bg-emerald-500" : "animate-pulse bg-amber-500"
                }`}
                style={{ width: 7, height: 7 }}
              />

              {isReady
                ? "LegalMind is ready"
                : "Please wait, our backend is getting ready…"}
            </div>
          </motion.div>

          <motion.h1
            variants={fadeUp}
            className="lm-home-hero-title font-serif"
            style={{
              fontSize: "clamp(3.25rem, 10vw, 8rem)",
              lineHeight: 0.98,
              marginTop: 40,
              letterSpacing: "-0.04em",
            }}
          >
            Legal research,
            <span className="block italic text-[#192957]">reimagined.</span>
          </motion.h1>

          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              alignItems: "flex-end",
              justifyContent: "space-between",
              gap: "32px 64px",
              marginTop: 48,
            }}
          >
            <motion.p
              variants={fadeUp}
              className="lm-home-lead text-lg text-[#6b6a68]"
              style={{ maxWidth: 520, lineHeight: 1.75 }}
            >
              Understand complex judgments, explore legal documents and discover
              reliable insights using multilingual artificial intelligence.
            </motion.p>

            <motion.div variants={fadeUp} style={{ ...layout.actions, marginTop: 0 }}>
              <motion.div
                whileHover={reduceMotion ? {} : { y: -2 }}
                whileTap={reduceMotion ? {} : { scale: 0.98 }}
              >
                <Link
                  to="/research"
                  className="lm-home-primary-cta rounded-full bg-[#192957] text-sm font-medium text-white transition hover:bg-[#223675]"
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 10,
                    padding: "16px 30px",
                  }}
                >
                  Start researching
                  <ArrowRight size={16} />
                </Link>
              </motion.div>

              <Link
                to="/register"
                className="lm-home-secondary-cta text-sm font-medium text-[#3d3929] underline decoration-[#d6d4cb] underline-offset-[6px] transition hover:decoration-[#192957]"
              >
                Create account
              </Link>
            </motion.div>
          </div>
        </motion.div>

        <motion.div {...reveal} style={{ paddingBottom: 24 }}>
          <ResearchPreview />
        </motion.div>
      </section>

      {/* Technology marquee */}

      <section
        className="lm-home-marquee lm-marquee border-y border-[#e8e6dc]"
        style={{ marginTop: 96, padding: "28px 0", overflow: "hidden" }}
        aria-label="Technology"
      >
        <div className="lm-marquee-track">
          {[...TECHNOLOGIES, ...TECHNOLOGIES].map((technology, index) => (
            <span
              key={`${technology}-${index}`}
              className="font-serif text-[#3d3929]"
              style={{
                fontSize: "clamp(1.25rem, 2.4vw, 1.75rem)",
                whiteSpace: "nowrap",
                display: "inline-flex",
                alignItems: "center",
                gap: 48,
                paddingRight: 48,
              }}
              aria-hidden={index >= TECHNOLOGIES.length}
            >
              {technology}
              <span className="text-[#192957]">✦</span>
            </span>
          ))}
        </div>
      </section>

      {/* Statement */}

      <section className="lm-home-column lm-home-section lm-home-column lm-home-section lm-home-column lm-home-section lm-home-column lm-home-section" style={{ ...layout.column, ...layout.section }}>
        <motion.div {...reveal}>
          <SectionLabel>Under the hood</SectionLabel>

          <h2
            className="font-serif"
            style={{ ...bigHeading, maxWidth: 920 }}
          >
            LegalMind reads what you upload, retrieves the passages that matter,
            and answers{" "}
            <span className="italic text-[#192957]">only from your documents.</span>
          </h2>

          <div
            style={{ display: "flex", flexWrap: "wrap", gap: 10, marginTop: 40 }}
          >
            {LANGUAGES.map((language) => (
              <span
                key={language}
                className="text-sm text-[#192957]"
                style={{
                  padding: "10px 20px",
                  borderRadius: 999,
                  border: "1px solid #192957",
                }}
              >
                {language}
              </span>
            ))}
          </div>
        </motion.div>
      </section>

      {/* Features */}

      <section
        id="features"
        className="scroll-mt-[90px] border-t border-[#e8e6dc]"
      >
        <div style={{ ...layout.column, ...layout.section }}>
          <motion.div
            {...reveal}
            style={{
              display: "flex",
              flexWrap: "wrap",
              alignItems: "flex-end",
              justifyContent: "space-between",
              gap: 32,
            }}
          >
            <div style={{ maxWidth: 640 }}>
              <SectionLabel>The LegalMind advantage</SectionLabel>

              <h2 className="font-serif" style={bigHeading}>
                Everything you need to research smarter.
              </h2>
            </div>

            <Link
              to="/research"
              className="text-sm font-medium text-[#192957]"
              style={{ display: "inline-flex", alignItems: "center", gap: 8 }}
            >
              Try it on your documents
              <ArrowUpRight size={16} />
            </Link>
          </motion.div>

          <motion.div
            variants={stagger}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.1 }}
            style={{ marginTop: 72 }}
            onMouseLeave={() => setActiveFeature(null)}
          >
            {FEATURES.map((feature, index) => {
              const Icon = feature.icon;
              const active = activeFeature === index;

              return (
                <motion.article
                  key={feature.title}
                  variants={fadeUp}
                  tabIndex={0}
                  onMouseEnter={() => setActiveFeature(index)}
                  onFocus={() => setActiveFeature(index)}
                  onBlur={() => setActiveFeature(null)}
                  className="lm-home-feature-row border-t border-[#e8e6dc] outline-none"
                  style={{
                    ...layout.featureRow,
                    opacity: activeFeature === null || active ? 1 : 0.45,
                    transition: "opacity 0.3s ease",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
                    <span
                      className="font-serif text-sm"
                      style={{ color: active ? "#192957" : "#83827d", width: 28 }}
                    >
                      {String(index + 1).padStart(2, "0")}
                    </span>

                    <span
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        width: 44,
                        height: 44,
                        borderRadius: 999,
                        background: active ? "#192957" : "#f0eee6",
                        color: active ? "#fff" : "#192957",
                        transition: "all 0.3s ease",
                        flexShrink: 0,
                      }}
                    >
                      <Icon size={18} strokeWidth={1.75} />
                    </span>

                    <h3
                      className="font-serif text-[#3d3929]"
                      style={{
                        fontSize: "clamp(1.5rem, 2.6vw, 2.1rem)",
                        letterSpacing: "-0.02em",
                        lineHeight: 1.15,
                      }}
                    >
                      {feature.title}
                    </h3>
                  </div>

                  <p
                    className="text-[15px] text-[#6b6a68]"
                    style={{ lineHeight: 1.75 }}
                  >
                    {feature.description}
                  </p>
                </motion.article>
              );
            })}
          </motion.div>
        </div>
      </section>

      {/* How it works */}

      <section
        id="how-it-works"
        className="scroll-mt-[90px] bg-[#f0eee6]"
      >
        <div style={{ ...layout.column, ...layout.section }}>
          <motion.div {...reveal} style={{ maxWidth: 640 }}>
            <SectionLabel>How it works</SectionLabel>

            <h2 className="font-serif" style={bigHeading}>
              From documents to answers.
            </h2>
          </motion.div>

          <motion.div
            variants={stagger}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            className="lm-home-steps"
            style={{ ...layout.stepsGrid, marginTop: 72 }}
          >
            {STEPS.map((step) => (
              <motion.div
                key={step.number}
                variants={fadeUp}
                whileHover={reduceMotion ? {} : { y: -6 }}
                style={{
                  background: "#faf9f5",
                  borderRadius: 24,
                  padding: 36,
                  minHeight: 280,
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                }}
              >
                <span
                  className="font-serif text-[#192957]"
                  style={{ fontSize: "clamp(3rem, 6vw, 4.5rem)", lineHeight: 1 }}
                >
                  {step.number}
                </span>

                <div>
                  <h3
                    className="font-serif"
                    style={{ fontSize: 30, letterSpacing: "-0.02em" }}
                  >
                    {step.title}
                  </h3>

                  <p
                    className="text-[15px] text-[#6b6a68]"
                    style={{ marginTop: 12, lineHeight: 1.75 }}
                  >
                    {step.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Closing call to action */}

      <section className="bg-[#192957] text-white">
        <div style={{ ...layout.column, ...layout.section }}>
          <motion.div {...reveal}>
            <SectionLabel light>Let’s begin</SectionLabel>

            <h2
              className="font-serif"
              style={{
                fontSize: "clamp(2.75rem, 8vw, 6.5rem)",
                lineHeight: 1,
                letterSpacing: "-0.04em",
                maxWidth: 960,
              }}
            >
              Bring your first document.{" "}
              <span className="italic text-white/60">Get a grounded answer.</span>
            </h2>

            <div style={{ ...layout.actions, marginTop: 56 }}>
              <motion.div
                whileHover={reduceMotion ? {} : { y: -2 }}
                whileTap={reduceMotion ? {} : { scale: 0.98 }}
              >
                <Link
                  to="/research"
                  className="lm-home-primary-cta rounded-full bg-white text-sm font-medium text-[#192957] transition hover:bg-[#f0eee6]"
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 10,
                    padding: "16px 30px",
                  }}
                >
                  Start researching
                  <ArrowRight size={16} />
                </Link>
              </motion.div>

              <Link
                to="/register"
                className="lm-home-secondary-cta text-sm font-medium text-white underline decoration-white/30 underline-offset-[6px] transition hover:decoration-white"
              >
                Create account
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}

      <footer className="bg-[#0f1a3d] text-white/60">
        <div
          className="lm-home-column lm-home-footer text-xs"
          style={{
            ...layout.column,
            padding: "32px",
            display: "flex",
            flexWrap: "wrap",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 16,
          }}
        >
          <span>© {new Date().getFullYear()} LegalMind AI</span>

          <span>
            AI-assisted research. Not a substitute for professional legal
            advice.
          </span>
        </div>
      </footer>
    </div>
  );
}

export default Home;