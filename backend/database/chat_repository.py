
from datetime import datetime, timezone

from database.supabase import get_supabase


class ChatRepository:

    def __init__(self):
        self.supabase = get_supabase()

    def create_chat(
        self,
        user_id: str,
        title: str = "New Chat",
        document_id: str | None = None
    ):
        chat_data = {
            "user_id": user_id,
            "title": title,
            "document_id": document_id
        }

        response = (
            self.supabase
            .table("chats")
            .insert(chat_data)
            .execute()
        )

        return response.data[0] if response.data else None

    def get_chat_for_user(
        self,
        chat_id: str,
        user_id: str
    ):
        response = (
            self.supabase
            .table("chats")
            .select("*")
            .eq("id", chat_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        return response.data[0] if response.data else None

    def get_chats_for_user(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ):
        response = (
            self.supabase
            .table("chats")
            .select("*", count="exact")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        return {
            "chats": response.data,
            "total_chats": response.count or 0
        }

    def add_message_for_user(
        self,
        chat_id: str,
        user_id: str,
        role: str,
        content: str
    ):
        if role not in {"user", "assistant"}:
            raise ValueError("Invalid message role.")

        # Verify conversation ownership first.
        chat = self.get_chat_for_user(
            chat_id=chat_id,
            user_id=user_id
        )

        if not chat:
            return None

        message_data = {
            "chat_id": chat_id,
            "role": role,
            "content": content
        }

        response = (
            self.supabase
            .table("messages")
            .insert(message_data)
            .execute()
        )

        # Update conversation activity.
        (
            self.supabase
            .table("chats")
            .update({
                "updated_at": datetime.now(timezone.utc).isoformat()
            })
            .eq("id", chat_id)
            .eq("user_id", user_id)
            .execute()
        )

        return response.data[0] if response.data else None

    def get_messages_for_chat(
        self,
        chat_id: str,
        user_id: str
    ):
        # Never retrieve messages without verifying ownership.
        chat = self.get_chat_for_user(
            chat_id=chat_id,
            user_id=user_id
        )

        if not chat:
            return None

        response = (
            self.supabase
            .table("messages")
            .select("*")
            .eq("chat_id", chat_id)
            .order("created_at", desc=False)
            .execute()
        )

        return response.data

    def update_chat_title(
        self,
        chat_id: str,
        user_id: str,
        title: str
    ):
        response = (
            self.supabase
            .table("chats")
            .update({
                "title": title,
                "updated_at": datetime.now(timezone.utc).isoformat()
            })
            .eq("id", chat_id)
            .eq("user_id", user_id)
            .execute()
        )

        return response.data[0] if response.data else None

    def delete_chat_for_user(
        self,
        chat_id: str,
        user_id: str
    ):
        response = (
            self.supabase
            .table("chats")
            .delete()
            .eq("id", chat_id)
            .eq("user_id", user_id)
            .execute()
        )

        return response.data[0] if response.data else None

    def update_chat_saved_status(self, chat_id: str, user_id: str, is_saved: bool):
        response = (
            self.supabase.table("chats")
            .update({"is_saved": is_saved})
            .eq("id", chat_id)
            .eq("user_id", user_id)
            .execute()
        )

        return response.data[0] if response.data else None


    def get_saved_chats_for_user(self, user_id: str, limit: int = 50):
        response = (
            self.supabase.table("chats")
            .select("id, title, document_id, is_saved, created_at, updated_at")
            .eq("user_id", user_id)
            .eq("is_saved", True)
            .order("updated_at", desc=True)
            .limit(limit)
            .execute()
        )

        return response.data