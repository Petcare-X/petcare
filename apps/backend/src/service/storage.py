from __future__ import annotations

import asyncio
import mimetypes
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import boto3
from botocore.client import BaseClient

from src.core.config import settings
from src.exceptions import AppError


class StorageService:
    def _ensure_configured(self) -> None:
        missing = [
            name
            for name, value in (
                ("MINIO_ENDPOINT", settings.MINIO_ENDPOINT),
                ("MINIO_ACCESS_KEY", settings.MINIO_ACCESS_KEY),
                ("MINIO_SECRET_KEY", settings.MINIO_SECRET_KEY),
                ("MINIO_BUCKET_PRIVATE", settings.MINIO_BUCKET_PRIVATE),
            )
            if not value
        ]
        if missing:
            raise AppError(
                message=f"MinIO is not configured: missing {', '.join(missing)}",
                status_code=500,
            )

    def _client(self) -> BaseClient:
        self._ensure_configured()
        session = boto3.session.Session()
        return session.client(
            "s3",
            endpoint_url=f"http{'s' if settings.MINIO_SECURE else ''}://{settings.MINIO_ENDPOINT}",
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            region_name=settings.MINIO_REGION or "us-east-1",
        )

    def _call_client(self, method_name: str, /, *args: Any, **kwargs: Any) -> Any:
        client = self._client()
        try:
            method = getattr(client, method_name)
            return method(*args, **kwargs)
        finally:
            client.close()

    def _download_bytes_sync(self, object_key: str) -> tuple[bytes, str | None]:
        client = self._client()
        try:
            response = client.get_object(
                Bucket=settings.MINIO_BUCKET_PRIVATE,
                Key=object_key,
            )
            body_stream = response["Body"]
            try:
                body = body_stream.read()
            finally:
                body_stream.close()
                release_conn = getattr(body_stream, "release_conn", None)
                if callable(release_conn):
                    release_conn()
            content_type = response.get("ContentType")
            return body, str(content_type) if content_type else None
        finally:
            client.close()

    def build_pet_photo_object_key(
        self,
        user_id: int,
        pet_id: int,
        content_type: str,
    ) -> str:
        ext = mimetypes.guess_extension(content_type) or ".bin"
        return f"users/{user_id}/pets/{pet_id}/photo/{uuid4().hex}{ext}"

    async def create_upload_url(self, object_key: str, content_type: str) -> str:
        assert settings.MINIO_BUCKET_PRIVATE is not None
        return await asyncio.to_thread(
            self._call_client,
            "generate_presigned_url",
            "put_object",
            Params={
                "Bucket": settings.MINIO_BUCKET_PRIVATE,
                "Key": object_key,
                "ContentType": content_type,
            },
            ExpiresIn=settings.MINIO_PRESIGNED_UPLOAD_TTL_SEC,
        )

    async def create_download_url(self, object_key: str) -> str:
        assert settings.MINIO_BUCKET_PRIVATE is not None
        return await asyncio.to_thread(
            self._call_client,
            "generate_presigned_url",
            "get_object",
            Params={
                "Bucket": settings.MINIO_BUCKET_PRIVATE,
                "Key": object_key,
            },
            ExpiresIn=settings.MINIO_PRESIGNED_DOWNLOAD_TTL_SEC,
        )

    async def head_object(self, object_key: str) -> dict[str, object]:
        assert settings.MINIO_BUCKET_PRIVATE is not None
        try:
            return await asyncio.to_thread(
                self._call_client,
                "head_object",
                Bucket=settings.MINIO_BUCKET_PRIVATE,
                Key=object_key,
            )
        except Exception as exc:
            raise AppError("Uploaded file is not found in storage", status_code=400) from exc

    async def delete_object(self, object_key: str) -> None:
        assert settings.MINIO_BUCKET_PRIVATE is not None
        await asyncio.to_thread(
            self._call_client,
            "delete_object",
            Bucket=settings.MINIO_BUCKET_PRIVATE,
            Key=object_key,
        )

    async def upload_bytes(
        self, object_key: str, payload: bytes, content_type: str
    ) -> dict[str, object]:
        assert settings.MINIO_BUCKET_PRIVATE is not None
        return await asyncio.to_thread(
            self._call_client,
            "put_object",
            Bucket=settings.MINIO_BUCKET_PRIVATE,
            Key=object_key,
            Body=payload,
            ContentType=content_type,
        )

    async def download_bytes(self, object_key: str) -> tuple[bytes, str | None]:
        assert settings.MINIO_BUCKET_PRIVATE is not None
        try:
            return await asyncio.to_thread(self._download_bytes_sync, object_key)
        except Exception as exc:
            raise AppError("Stored file is not available", status_code=404) from exc

    @staticmethod
    def now_utc() -> datetime:
        return datetime.now(timezone.utc)

    def build_pet_document_object_key(
        self,
        user_id: int,
        pet_id: int,
        document_type_id: int,
        filename: str,
        content_type: str,
    ) -> str:
        ext = mimetypes.guess_extension(content_type) or ""
        safe_name = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        return f"users/{user_id}/pets/{pet_id}/documents/{document_type_id}/{uuid4().hex}_{safe_name or 'file'}{ext}"
