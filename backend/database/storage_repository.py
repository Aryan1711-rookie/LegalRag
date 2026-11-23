import os
from pathlib import Path
from uuid import UUID

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


class StorageRepository:

    MAX_FILE_SIZE = 20 * 1024 * 1024

    MIME_TYPES = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg"
    }

    def __init__(self):
        self.supabase = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SECRET_KEY"]
        )

        self.bucket_name = os.getenv(
            "SUPABASE_STORAGE_BUCKET",
            "legal-documents"
        )

        self.bucket = self.supabase.storage.from_(
            self.bucket_name
        )

    def build_object_path(
        self,
        user_id: str,
        document_id: str,
        extension: str
    ) -> str:

        user_id = str(UUID(user_id))
        document_id = str(UUID(document_id))
        extension = extension.lower()

        if extension not in self.MIME_TYPES:
            raise ValueError("Unsupported file type.")

        return (
            f"{user_id}/"
            f"{document_id}/"
            f"original{extension}"
        )

    def upload_document(
        self,
        file_path: str,
        user_id: str,
        document_id: str
    ) -> str:

        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(file_path)

        if path.stat().st_size > self.MAX_FILE_SIZE:
            raise ValueError("File exceeds the 20 MB limit.")

        extension = path.suffix.lower()

        object_path = self.build_object_path(
            user_id=user_id,
            document_id=document_id,
            extension=extension
        )

        with path.open("rb") as file:
            self.bucket.upload(
                path=object_path,
                file=file,
                file_options={
                    "content-type": self.MIME_TYPES[extension],
                    "upsert": "false"
                }
            )

        return object_path

    def download_document(
        self,
        user_id: str,
        document_id: str,
        extension: str,
        destination: str
    ) -> Path:

        object_path = self.build_object_path(
            user_id,
            document_id,
            extension
        )

        file_data = self.bucket.download(object_path)

        destination = Path(destination)

        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        destination.write_bytes(file_data)

        return destination

    def delete_document(
        self,
        user_id: str,
        document_id: str,
        extension: str
    ):

        object_path = self.build_object_path(
            user_id,
            document_id,
            extension
        )

        return self.bucket.remove([object_path])