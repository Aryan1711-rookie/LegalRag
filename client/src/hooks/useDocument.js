import { useEffect, useState } from "react";
import { getDocument } from "../services/document.js";

export default function useDocumentProgress(documentId) {
  const [document, setDocument] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!documentId) return;

    let cancelled = false;
    let timer;

    const controller = new AbortController();

    setDocument(null);
    setError("");

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
          result.status !== "completed" &&
          result.status !== "failed"
        ) {
          timer = setTimeout(poll, 2000);
        }
      } catch (error) {
        if (cancelled || error.name === "AbortError") {
          return;
        }

        setError(error.message);
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