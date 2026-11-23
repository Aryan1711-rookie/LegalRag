import { motion, useReducedMotion } from "framer-motion";

function Preloader() {
  const reduceMotion = useReducedMotion();

  return (
    <motion.div
      initial={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{
        duration: reduceMotion ? 0 : 0.7,
        ease: "easeInOut",
      }}
      className="fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-[#faf9f5]"
    >
      {/* Loading animation */}
      <video
        src={`${import.meta.env.BASE_URL}animations/loader.webm`}
        autoPlay={!reduceMotion}
        loop={!reduceMotion}
        muted
        playsInline
        preload="auto"
        className="h-[250px] w-[250px] object-contain"
        aria-hidden="true"
      />

      <motion.h1
        initial={{ opacity: 0, y: reduceMotion ? 0 : 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: reduceMotion ? 0 : 0.3 }}
        className="mt-4 font-serif text-3xl text-[#3d3929]"
      >
        LegalMind AI
      </motion.h1>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: reduceMotion ? 0 : 0.6 }}
        className="mt-3 text-sm text-[#83827d]"
      >
        Preparing your research experience...
      </motion.p>
    </motion.div>
  );
}

export default Preloader;