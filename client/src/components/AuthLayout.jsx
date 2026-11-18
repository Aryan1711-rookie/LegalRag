
import { Scale, ShieldCheck, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

function AuthLayout({ children, title, subtitle, footer }) {
  return (
    <div className="min-h-screen bg-white lg:grid lg:grid-cols-2">
      {/* Left branding panel */}
      <section className="relative hidden overflow-hidden bg-[#192b5b] p-12 text-white lg:flex lg:flex-col lg:justify-between">
        <div className="absolute -right-32 -top-32 h-96 w-96 rounded-full border border-white/10" />
        <div className="absolute -bottom-40 -left-32 h-96 w-96 rounded-full border border-white/10" />

        <Link to="/" className="relative z-10 flex items-center gap-3">
          <div className="rounded-xl bg-white/10 p-3">
            <Scale size={28} />
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">
              LegalMind
            </h1>
            <p className="text-xs tracking-[0.2em] text-blue-200">
              LEGAL INTELLIGENCE
            </p>
          </div>
        </Link>

        <div className="relative z-10 max-w-lg">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm text-blue-100">
            <Sparkles size={15} />
            AI-powered legal research
          </div>

          <h2 className="text-4xl font-semibold leading-tight xl:text-5xl">
            Research law.
            <br />
            Understand precedents.
            <br />
            <span className="text-blue-300">Think with clarity.</span>
          </h2>

          <p className="mt-6 max-w-md text-base leading-7 text-blue-100/80">
            Your intelligent legal research workspace. Explore legal
            documents, discover relevant judgments, and get grounded
            answers from your sources.
          </p>

          <div className="mt-10 flex items-center gap-3 rounded-xl border border-white/15 bg-white/5 p-4">
            <ShieldCheck className="shrink-0 text-blue-300" size={24} />
            <div>
              <p className="text-sm font-medium">Your research workspace</p>
              <p className="mt-1 text-xs text-blue-100/70">
                Organised, accessible, and built for focused research.
              </p>
            </div>
          </div>
        </div>

        <p className="relative z-10 text-xs text-blue-200/60">
          © {new Date().getFullYear()} LegalMind. All rights reserved.
        </p>
      </section>

      {/* Right authentication panel */}
      <section className="flex min-h-screen flex-col items-center justify-center px-6 py-10 sm:px-12">
        <div className="mb-10 flex items-center gap-3 lg:hidden">
          <div className="rounded-xl bg-[#192b5b] p-3 text-white">
            <Scale size={25} />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-[#192b5b]">
              LegalMind
            </h1>
            <p className="text-[10px] tracking-[0.2em] text-slate-500">
              LEGAL INTELLIGENCE
            </p>
          </div>
        </div>

        <div className="w-full max-w-md">
          <div className="mb-8">
            <p className="mb-3 text-sm font-medium text-blue-700">
              LEGALMIND WORKSPACE
            </p>
            <h2 className="text-3xl font-semibold tracking-tight text-slate-900">
              {title}
            </h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              {subtitle}
            </p>
          </div>

          {children}

          <div className="mt-8 text-center text-sm text-slate-500">
            {footer}
          </div>
        </div>

        <p className="mt-12 text-xs text-slate-400">
          Secure access to your legal research workspace
        </p>
      </section>
    </div>
  );
}

export default AuthLayout;
