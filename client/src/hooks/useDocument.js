import { useEffect, useState } from "react";
import { getDocument } from "../services/document.js";

export default function useDocumentProgress(documentId) {
  const [document, setDocument] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setDocument(null);
    setError("");

    if (!documentId) return;

    let cancelled = false;
    let timer;

    const controller = new AbortController();

    async function poll() {
      try {
        const result = await getDocument(
          documentId,
          controller.signal
        );

        if (cancelled) return;

        setDocument(result);
        setError("");

        if (
          ["queued", "processing"].includes(result.status)
        ) {
          timer = setTimeout(
            poll,
            result.status === "queued" ? 5000 : 2000
          );
        }
      } catch (error) {
        if (cancelled || error.name === "AbortError") {
          return;
        }

        setError(error.message);

        // Recover from temporary connection failures.
        timer = setTimeout(poll, 5000);
      }
    }

    poll();

    return () => {
      cancelled = true;
      clearTimeout(timer);
      controller.abort();
    };
  }, [documentId]);

  return { document, error };
}