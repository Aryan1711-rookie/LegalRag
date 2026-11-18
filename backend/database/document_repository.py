
from database.supabase import get_supabase


class DocumentRepository:

    def __init__(self):
        self.supabase = get_supabase()

    def create_document(
    self,
    title: str,
    file_name: str,
    total_pages: int,
    user_id: str,
    file_path: str | None = None,
    status: str = "processing"
    ):
        document_data = {
            "title": title,
            "file_name": file_name,
            "file_path": file_path,
            "total_pages": total_pages,
            "user_id": user_id,
            "status": status
        }

        response = (
            self.supabase
            .table("documents")
            .insert(document_data)
            .execute()
        )

        return response.data[0]

    def insert_chunks(
        self,
        document_id: str,
        chunks: list[dict],
        batch_size: int = 50
    ):
        records = []

        for chunk in chunks:
            records.append({
                "document_id": document_id,
                "chunk_id": chunk["chunk_id"],
                "content": chunk["text"],
                "retrieval_text": chunk["retrieval_text"],
                "metadata": chunk["metadata"],
                "embedding": chunk["embedding"]
            })

        inserted_count = 0

        try:
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]

                response = (
                    self.supabase
                    .table("document_chunks")
                    .insert(batch)
                    .execute()
                )

                inserted_count += len(response.data)

            return inserted_count

        
        except Exception:
            try:
                (
                    self.supabase
                    .table("document_chunks")
                    .delete()
                    .eq("document_id", document_id)
                    .execute()
                )
            except Exception as cleanup_error:
                print(
                    f"WARNING: Chunk cleanup failed for "
                    f"{document_id}: {cleanup_error}"
                )

            raise


    def delete_document(self, document_id: str):
        response = (
            self.supabase
            .table("documents")
            .delete()
            .eq("id", document_id)
            .execute()
        )

        return response.data


    def get_document_for_user(
        self,
        document_id: str,
        user_id: str
    ):
        response = (
            self.supabase
            .table("documents")
            .select("id, title, user_id")
            .eq("id", document_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        return response.data[0] if response.data else None
    
    
   
    def get_documents_for_user(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
        search: str | None = None,
        status: str | None = None
    ):
        query = (
            self.supabase
            .table("documents")
            .select(
                "id, title, file_name, total_pages, status, created_at",
                count="exact"
            )
            .eq("user_id", user_id)
        )

        if search:
            query = query.ilike("title", f"%{search}%")

        if status:
            if status not in {"processing", "completed", "failed"}:
                raise ValueError("Invalid document status.")

            query = query.eq("status", status)

        response = (
            query
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        return {
            "documents": response.data,
            "total_documents": response.count or 0
        }



    def get_document_for_user(
        self,
        document_id: str,
        user_id: str
    ):
        response = (
            self.supabase
            .table("documents")
            .select(
                "id, title, file_name, total_pages,status, created_at"
            )
            .eq("id", document_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        return response.data[0] if response.data else None

    # def delete_document_for_user(
    #     self,
    #     document_id: str,
    #     user_id: str
    # ):
    #     # Verify ownership before deleting anything.
    #     document = self.get_document_for_user(
    #         document_id=document_id,
    #         user_id=user_id
    #     )

    #     if not document:
    #         return None

    #     # Delete associated chunks first.
    #     self.supabase \
    #         .table("document_chunks") \
    #         .delete() \
    #         .eq("document_id", document_id) \
    #         .execute()

    #     # Delete the owned document.
    #     response = (
    #         self.supabase
    #         .table("documents")
    #         .delete()
    #         .eq("id", document_id)
    #         .eq("user_id", user_id)
    #         .execute()
    #     )

    #     return response.data[0] if response.data else None

    def delete_document_for_user(
        self,
        document_id: str,
        user_id: str
    ):
        response = (
            self.supabase
            .table("documents")
            .delete()
            .eq("id", document_id)
            .eq("user_id", user_id)
            .execute()
        )

        return response.data[0] if response.data else None

    def update_document_status(
    self,
    document_id: str,
    status: str
    ):
        if status not in {"processing", "completed", "failed"}:
            raise ValueError("Invalid document status.")

        response = (
            self.supabase
            .table("documents")
            .update({"status": status})
            .eq("id", document_id)
            .execute()
        )

        return response.data[0] if response.data else None
