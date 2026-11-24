
import { apiFetch } from "./apiFetch.js";

export async function searchWebResearch(query) {
  const token = sessionStorage.getItem("access_token");

  if (!token) {
    throw new Error("Please log in to use Web Research.");
  }

  const response = await apiFetch(
    "/api/v1/web-research/search",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        query: query.trim(),
      }),
    }
  );

  const contentType =
    response.headers.get("content-type") || "";

  if (!contentType.includes("application/json")) {
    throw new Error(
      "Web Research received an invalid server response."
    );
  }

  const data = await response.json();

  if (!response.ok) {
    const detail = data.detail;

    throw new Error(
      typeof detail === "string"
        ? detail
        : `Web research failed (HTTP ${response.status})`
    );
  }

  return data;
}
