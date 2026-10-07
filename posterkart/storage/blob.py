import os

from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.core.exceptions import SuspiciousOperation

from vercel import blob


class VercelBlobStorage(Storage):
    """
    Django storage backend for Vercel Blob.
    """

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.token = os.environ.get("BLOB_READ_WRITE_TOKEN")

        if not self.token:
            raise RuntimeError(
                "BLOB_READ_WRITE_TOKEN environment variable is not set."
            )

        self.base_url = os.environ.get(
            "BLOB_PUBLIC_BASE_URL",
            "https://c2i4hw2qmjoobtor.public.blob.vercel-storage.com",
        )

    def _save(self, name, content):
        name = name.replace("\\", "/")

        blob_path = f"posterkart/{name}"

        data = content.read()

        result = blob.put(
            blob_path,
            data,
            access="public",
            token=self.token,
        )

        return name

    def _open(self, name, mode="rb"):
        if "r" not in mode:
            raise ValueError("VercelBlobStorage only supports reading.")

        url = self.url(name)

        import requests

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        return ContentFile(response.content)

    def delete(self, name):
        blob_path = f"posterkart/{name}"

        try:
            blob.delete(
                blob_path,
                token=self.token,
            )
        except Exception:
            pass

    def exists(self, name):
        blob_path = f"posterkart/{name}"

        try:
            blob.head(
                blob_path,
                token=self.token,
            )
            return True
        except Exception:
            return False

    def url(self, name):
        name = name.replace("\\", "/")

        return f"{self.base_url}/posterkart/{name}"

    def size(self, name):
        blob_path = f"posterkart/{name}"

        result = blob.head(
            blob_path,
            token=self.token,
        )

        return result.size