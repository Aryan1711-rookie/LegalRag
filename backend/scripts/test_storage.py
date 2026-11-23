import argparse
import hashlib

from pathlib import Path
from uuid import uuid4
from tempfile import TemporaryDirectory

from database.storage_repository import StorageRepository


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    args = parser.parse_args()

    storage = StorageRepository()

    source = Path(args.file)

    user_id = str(uuid4())
    document_id = str(uuid4())
    uploaded = False

    print("\n========== STORAGE TEST ==========")

    try:
        object_path = storage.upload_document(
            file_path=str(source),
            user_id=user_id,
            document_id=document_id
        )

        uploaded = True

        print("Upload successful.")
        print("Object path:", object_path)

        with TemporaryDirectory() as temp_dir:

            destination = Path(temp_dir) / source.name

            downloaded = storage.download_document(
                user_id=user_id,
                document_id=document_id,
                extension=source.suffix,
                destination=str(destination)
            )

            print("Download successful.")

            original_hash = hashlib.sha256(
                source.read_bytes()
            ).hexdigest()

            downloaded_hash = hashlib.sha256(
                downloaded.read_bytes()
            ).hexdigest()

            if original_hash != downloaded_hash:
                raise RuntimeError("File integrity check failed.")

            print("File integrity: PASSED")

    finally:

        if uploaded:
            storage.delete_document(
                user_id=user_id,
                document_id=document_id,
                extension=source.suffix
            )

            print("Test file deleted.")

    print("Storage test completed successfully.")


if __name__ == "__main__":
    main()