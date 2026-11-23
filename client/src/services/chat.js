
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export async function askQuestion(
  question,
  documentId,
  chatId = null
) {
  const accessToken = sessionStorage.getItem("access_token");

  if (!accessToken) {
    throw new Error("You must be logged in to use LegalMind AI.");
  }

  let response;

  try {
    response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        question,
        document_id: documentId,
        chat_id: chatId,
      }),
    });
  } catch {
    throw new Error(
      "Cannot connect to the server. Check whether the backend is running."
    );
  }

  const data = await response.json().catch(() => ({}));

  if (response.status === 401) {
    throw new Error("Your session has expired. Please log in again.");
  }

  if (!response.ok) {
    throw new Error(data.detail || "Unable to process your question.");
  }

  return data;
}
export async function getSavedChats() {
  const accessToken = sessionStorage.getItem("access_token");

  if (!accessToken) {
    throw new Error("Please log in again.");
  }

  const response = await fetch(
    `${API_BASE_URL}/api/v1/chats/saved`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || "Failed to fetch saved chats.");
  }

  return data;
}


export async function updateChatSavedStatus(chatId, isSaved) {
  const accessToken = sessionStorage.getItem("access_token");

  if (!accessToken) {
    throw new Error("Please log in again.");
  }

  const response = await fetch(
    `${API_BASE_URL}/api/v1/chats/${chatId}/saved`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        is_saved: isSaved,
      }),
    }
  );

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || "Failed to update saved status.");
  }

  return data;
}


export async function getChatMessages(chatId) {
  const accessToken = sessionStorage.getItem("access_token");

  if (!accessToken) {
    throw new Error("Please log in again.");
  }

  const response = await fetch(
    `${API_BASE_URL}/api/v1/chats/${chatId}/messages`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || "Failed to load chat history.");
  }

  return data;
}
