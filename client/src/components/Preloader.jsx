
import { useEffect, useState } from "react";
import {
  AnimatePresence,
  motion,
  useReducedMotion,
} from "framer-motion";
import {
  BrainCircuit,
  Scale,
  Sparkles,
} from "lucide-react";

const EASE = [0.22, 1, 0.36, 1];

const PARTICLES = Array.from({ length: 28 }, (_, i) => {
  const angle = (i / 28) * Math.PI * 2;
  const radius = 115 + (i % 4) * 20;

  return {
    id: i,
    x: Math.cos(angle) * radius,
    y: Math.sin(angle) * radius,
    size: i % 5 === 0 ? 4 : 2,
    delay: (i % 7) * 0.12,
  };
});

function OrbitalRing({
  size,
  duration,
  reverse = false,
  delay = 0,
  reduceMotion,
  className = "",
}) {
  return (
    <motion.div
      className={`absolute rounded-full border ${className}`}
      style={{
        width: size,
        height: size,
        borderColor: "rgba(173, 139, 78, 0.23)",
      }}
      initial={{
        opacity: 0,
        scale: reduceMotion ? 1 : 0.65,
        rotate: 0,
      }}
      animate={{
        opacity: 1,
        scale: 1,
        rotate: reduceMotion ? 0 : reverse ? -360 : 360,
      }}
      transition={{
        opacity: { duration: 1, delay },
        scale: { duration: 1.4, delay, ease: EASE },
        rotate: {
          duration,
          repeat: reduceMotion ? 0 : Infinity,
          ease: "linear",
        },
      }}
    >
      <div className="absolute -top-[3px] left-1/2 h-[6px] w-[6px] -translate-x-1/2 rounded-full bg-[#b9955c] shadow-[0_0_14px_4px_rgba(185,149,92,0.35)]" />

      <div className="absolute bottom-[12%] right-[12%] h-[4px] w-[4px] rounded-full bg-[#d6bd91]" />

      <div className="absolute inset-3 rounded-full border border-dashed border-[#b9955c]/10" />
    </motion.div>
  );
}

function NeuralCore({ reduceMotion }) {
  return (
    <div className="relative flex h-[340px] w-[340px] items-center justify-center sm:h-[420px] sm:w-[420px]">
      {/* Ambient glow */}
      <motion.div
        className="absolute h-[260px] w-[260px] rounded-full"
        style={{
          background:
            "radial-gradient(circle, rgba(201,167,105,0.18) 0%, rgba(201,167,105,0.05) 45%, transparent 72%)",
          filter: "blur(20px)",
        }}
        animate={{
          scale: reduceMotion ? 1 : [1, 1.25, 1],
          opacity: reduceMotion ? 0.7 : [0.5, 0.9, 0.5],
        }}
        transition={{
          duration: 4,
          repeat: reduceMotion ? 0 : Infinity,
          ease: "easeInOut",
        }}
      />

      {/* Orbital architecture */}
      <OrbitalRing
        size={190}
        duration={12}
        delay={0.1}
        reduceMotion={reduceMotion}
        className="border-dashed"
      />

      <OrbitalRing
        size={260}
        duration={18}
        reverse
        delay={0.25}
        reduceMotion={reduceMotion}
      />

      <OrbitalRing
        size={330}
        duration={28}
        delay={0.4}
        reduceMotion={reduceMotion}
        className="border-dotted"
      />

      {/* Elliptical orbital rings */}
      <motion.div
        className="absolute h-[120px] w-[310px] rounded-[50%] border border-[#b9955c]/30"
        style={{ transform: "rotate(-35deg)" }}
        initial={{ opacity: 0, scale: 0.5 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1.5, ease: EASE }}
      />

      <motion.div
        className="absolute h-[310px] w-[120px] rounded-[50%] border border-[#b9955c]/20"
        style={{ transform: "rotate(-35deg)" }}
        initial={{ opacity: 0, scale: 0.5 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1.5, delay: 0.2, ease: EASE }}
      />

      {/* Particle field */}
      {PARTICLES.map((particle) => (
        <motion.div
          key={particle.id}
          className="absolute rounded-full bg-[#b9955c]"
          style={{
            width: particle.size,
            height: particle.size,
          }}
          initial={{
            x: 0,
            y: 0,
            opacity: 0,
            scale: 0,
          }}
          animate={{
            x: particle.x,
            y: particle.y,
            opacity: reduceMotion ? 0.5 : [0.2, 0.8, 0.2],
            scale: 1,
          }}
          transition={{
            x: { duration: 1.6, delay: particle.delay, ease: EASE },
            y: { duration: 1.6, delay: particle.delay, ease: EASE },
            scale: { duration: 1, delay: particle.delay },
            opacity: {
              duration: 3,
              delay: particle.delay,
              repeat: reduceMotion ? 0 : Infinity,
              ease: "easeInOut",
            },
          }}
        />
      ))}

      {/* Central glass core */}
      <motion.div
        className="relative z-10 flex h-[116px] w-[116px] items-center justify-center rounded-full border border-[#c5a46e]/40 bg-[#faf9f5]/80 shadow-[0_0_60px_rgba(185,149,92,0.18),inset_0_0_35px_rgba(185,149,92,0.08)] backdrop-blur-xl"
        initial={{
          opacity: 0,
          scale: reduceMotion ? 1 : 0,
          rotate: reduceMotion ? 0 : -120,
        }}
        animate={{
          opacity: 1,
          scale: 1,
          rotate: 0,
        }}
        transition={{
          duration: 1.4,
          delay: 0.3,
          ease: EASE,
        }}
      >
        {/* Core pulse */}
        <motion.div
          className="absolute inset-[-12px] rounded-full border border-[#b9955c]/25"
          animate={{
            scale: reduceMotion ? 1 : [1, 1.2, 1],
            opacity: reduceMotion ? 0.5 : [0.6, 0, 0.6],
          }}
          transition={{
            duration: 3,
            repeat: reduceMotion ? 0 : Infinity,
          }}
        />

        <motion.div
          animate={
            reduceMotion
              ? {}
              : {
                  scale: [1, 1.08, 1],
                  rotate: [0, 3, -3, 0],
                }
          }
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          <BrainCircuit
            size={52}
            strokeWidth={1.2}
            className="text-[#9f7b43]"
          />
        </motion.div>

        <motion.div
          className="absolute -right-2 -top-2"
          animate={
            reduceMotion
              ? {}
              : {
                  rotate: [0, 20, 0],
                  scale: [1, 1.25, 1],
                }
          }
          transition={{
            duration: 3,
            repeat: Infinity,
          }}
        >
          <Sparkles size={22} className="text-[#b9955c]" />
        </motion.div>
      </motion.div>

      {/* Horizontal scanning beam */}
      {!reduceMotion && (
        <motion.div
          className="pointer-events-none absolute z-20 h-[2px] w-[290px]"
          style={{
            background:
              "linear-gradient(90deg, transparent, rgba(185,149,92,0.7), transparent)",
            boxShadow: "0 0 24px rgba(185,149,92,0.25)",
          }}
          initial={{ y: -145, opacity: 0 }}
          animate={{
            y: [-145, 145],
            opacity: [0, 0.8, 0],
          }}
          transition={{
            duration: 3.8,
            delay: 1.1,
            repeat: Infinity,
            repeatDelay: 1,
            ease: "easeInOut",
          }}
        />
      )}
    </div>
  );
}

function LoadingText({ reduceMotion }) {
  const messages = [
    "Initializing neural research engine",
    "Connecting legal intelligence",
    "Preparing your research workspace",
    "Almost ready",
  ];

  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (reduceMotion) return;

    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % messages.length);
    }, 2200);

    return () => clearInterval(interval);
  }, [reduceMotion]);

  return (
    <div className="flex h-7 items-center justify-center">
      <AnimatePresence mode="wait">
        <motion.p
          key={index}
          initial={{ opacity: 0, y: reduceMotion ? 0 : 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: reduceMotion ? 0 : -8 }}
          transition={{ duration: reduceMotion ? 0 : 0.35 }}
          className="text-center text-xs tracking-[0.15em] text-[#8b877c] sm:text-sm"
        >
          {reduceMotion ? messages[2] : messages[index]}
        </motion.p>
      </AnimatePresence>
    </div>
  );
}

export default function Preloader() {
  const reduceMotion = useReducedMotion();

  return (
    <motion.div
      initial={{ opacity: 1 }}
      exit={{
        opacity: 0,
        scale: reduceMotion ? 1 : 1.06,
        filter: reduceMotion ? "none" : "blur(16px)",
      }}
      transition={{
        duration: reduceMotion ? 0 : 0.85,
        ease: EASE,
      }}
      className="fixed inset-0 z-[9999] flex h-[100dvh] w-full flex-col overflow-hidden bg-[#faf9f5]"
      role="status"
      aria-label="Loading LegalMind AI"
      aria-live="polite"
    >
      {/* Reserve independent space for the animated core at every viewport size. */}
      <style>{`
        .lm-preloader-core-slot { height: 340px; width: 100%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .lm-preloader-core-inner { transform: scale(.80); transform-origin: center; }
        @media (max-width: 639px) {
          .lm-preloader-core-slot { height: 245px; }
          .lm-preloader-core-inner { transform: scale(.68); }
        }
        @media (max-height: 680px) {
          .lm-preloader-core-slot { height: 205px; }
          .lm-preloader-core-inner { transform: scale(.55); }
          .lm-preloader-version { display: none; }
        }
        @media (max-height: 520px) {
          .lm-preloader-core-slot { height: 150px; }
          .lm-preloader-core-inner { transform: scale(.40); }
        }
      `}</style>

      {/* Architectural background grid */}
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.18]"
        style={{
          backgroundImage: `
            linear-gradient(to right, #c2b69d 1px, transparent 1px),
            linear-gradient(to bottom, #c2b69d 1px, transparent 1px)
          `,
          backgroundSize: "64px 64px",
          maskImage:
            "radial-gradient(ellipse at center, black, transparent 75%)",
          WebkitMaskImage:
            "radial-gradient(ellipse at center, black, transparent 75%)",
        }}
      />

      {/* Corner framing */}
      <div className="absolute left-6 top-6 h-12 w-12 border-l border-t border-[#b9955c]/35 sm:left-10 sm:top-10" />
      <div className="absolute right-6 top-6 h-12 w-12 border-r border-t border-[#b9955c]/35 sm:right-10 sm:top-10" />
      <div className="absolute bottom-6 left-6 h-12 w-12 border-b border-l border-[#b9955c]/35 sm:bottom-10 sm:left-10" />
      <div className="absolute bottom-6 right-6 h-12 w-12 border-b border-r border-[#b9955c]/35 sm:bottom-10 sm:right-10" />

      {/* Top system status */}
      <motion.div
        className="pointer-events-none absolute top-5 left-4 right-4 flex items-center justify-center gap-3 sm:top-10"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.8 }}
      >
        <motion.div
          className="h-[6px] w-[6px] rounded-full bg-[#b9955c]"
          animate={{
            opacity: reduceMotion ? 1 : [0.3, 1, 0.3],
          }}
          transition={{
            duration: 1.5,
            repeat: reduceMotion ? 0 : Infinity,
          }}
        />
        <span className="font-mono text-[9px] uppercase tracking-[0.3em] text-[#9a907e] sm:text-[10px]">
          Intelligence System / Boot Sequence
        </span>
      </motion.div>

      {/* Main visualization */}
      <motion.div
        className="relative z-10 mx-auto flex w-full min-h-0 flex-1 flex-col items-center overflow-y-auto overflow-x-hidden px-4 pt-16 pb-10 sm:pt-20 sm:pb-14"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.7 }}
      >
        <div className="lm-preloader-core-slot">
          <div className="lm-preloader-core-inner">
            <NeuralCore reduceMotion={reduceMotion} />
          </div>
        </div>

        {/* Brand reveal */}
        <motion.div
          className="flex shrink-0 flex-col items-center text-center"
          initial={{
            opacity: 0,
            y: reduceMotion ? 0 : 28,
            filter: reduceMotion ? "none" : "blur(10px)",
          }}
          animate={{
            opacity: 1,
            y: 0,
            filter: "blur(0px)",
          }}
          transition={{
            duration: 1,
            delay: reduceMotion ? 0 : 0.9,
            ease: EASE,
          }}
        >
          <div className="mb-4 flex items-center gap-3">
            <div className="h-px w-10 bg-gradient-to-r from-transparent to-[#b9955c]" />
            <Scale size={17} strokeWidth={1.3} className="text-[#b9955c]" />
            <div className="h-px w-10 bg-gradient-to-l from-transparent to-[#b9955c]" />
          </div>

          <h1 className="font-serif text-[clamp(1.8rem,8vw,3.75rem)] leading-tight tracking-[-0.045em] text-[#353326]">
            LegalMind{" "}
            <span className="font-light italic text-[#a78651]">AI</span>
          </h1>

          <motion.div
            className="mt-5 h-px bg-gradient-to-r from-transparent via-[#b9955c] to-transparent"
            initial={{ width: 0 }}
            animate={{ width: 210 }}
            transition={{ duration: 1.2, delay: 1.3, ease: EASE }}
          />

          <p className="mt-4 max-w-full px-2 text-center font-mono text-[9px] uppercase tracking-[0.18em] text-[#a09a8c] sm:tracking-[0.35em] sm:text-[10px]">
            Where Law Meets Intelligence
          </p>
        </motion.div>
      </motion.div>

      {/* Loading progress */}
      <motion.div
        className="mt-7 flex w-full max-w-[340px] shrink-0 flex-col items-center gap-4 px-3 sm:mt-10"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.1, duration: 0.8 }}
      >
        <LoadingText reduceMotion={reduceMotion} />

        <div className="relative h-[2px] w-full overflow-hidden rounded-full bg-[#dcd5c7]">
          <motion.div
            className="absolute inset-y-0 left-0 w-[35%] rounded-full bg-gradient-to-r from-[#c8a971] via-[#92703d] to-[#c8a971]"
            animate={
              reduceMotion
                ? { x: "90%" }
                : { x: ["-110%", "310%"] }
            }
            transition={{
              duration: 2,
              repeat: reduceMotion ? 0 : Infinity,
              ease: "easeInOut",
            }}
          />
        </div>

        <div className="flex w-full items-center justify-between font-mono text-[9px] uppercase tracking-[0.2em] text-[#aaa394]">
          <span>System Initialization</span>
          <span>LM / AI</span>
        </div>
      </motion.div>

      {/* Version metadata */}
      <div className="lm-preloader-version pointer-events-none absolute bottom-3 left-0 right-0 text-center font-mono text-[9px] tracking-[0.2em] text-[#c0b8a9]">
        LEGALMIND INTELLIGENCE ENGINE
      </div>
    </motion.div>
  );
}
