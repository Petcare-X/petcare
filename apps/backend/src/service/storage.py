from __future__ import annotations

import asyncio
import mimetypes
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import boto3
from botocore.client import BaseClient

from src.core.config import settings
from src.exceptions import AppError


@dataclass(frozen=True, slots=True)
class StoredObjectMeta:
    content_type: str | None
    size_bytes: int | None
    etag: str | None


class StorageService:
    @staticmethod
    def build_pet_document_custom_name(document_name: str, sequence_number: int = 0) -> str:
        safe_name = re.sub(r"\s+", "_", document_name.strip().lower())
        safe_name = re.sub(r"[^0-9A-Za-zА-Яа-яЁё_-]", "", safe_name).strip("_")
        base_name = safe_name or "document"
        return f"{base_name}_{sequence_number}" if sequence_number > 0 else base_name

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
        return f"{self.build_pet_photo_prefix(user_id=user_id, pet_id=pet_id)}{uuid4().hex}{ext}"

    @staticmethod
    def build_pet_photo_prefix(*, user_id: int, pet_id: int) -> str:
        return f"users/{user_id}/pets/{pet_id}/photo/"

    @staticmethod
    def build_pet_document_prefix(*, user_id: int, pet_id: int, document_type_id: int) -> str:
        return f"users/{user_id}/pets/{pet_id}/documents/{document_type_id}/"

    def is_pet_photo_key(self, object_key: str, *, user_id: int, pet_id: int) -> bool:
        return object_key.startswith(self.build_pet_photo_prefix(user_id=user_id, pet_id=pet_id))

    def is_pet_document_key(
        self,
        object_key: str,
        *,
        user_id: int,
        pet_id: int,
        document_type_id: int,
    ) -> bool:
        return object_key.startswith(
            self.build_pet_document_prefix(
                user_id=user_id,
                pet_id=pet_id,
                document_type_id=document_type_id,
            )
        )

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

    async def get_object_meta(self, object_key: str) -> StoredObjectMeta:
        head = await self.head_object(object_key)
        content_type = head.get("ContentType")
        size_bytes_raw = head.get("ContentLength")
        etag_raw = head.get("ETag")
        return StoredObjectMeta(
            content_type=str(content_type) if content_type else None,
            size_bytes=int(size_bytes_raw) if isinstance(size_bytes_raw, int | float) else None,
            etag=str(etag_raw).strip('"') if etag_raw is not None else None,
        )

    async def delete_object(self, object_key: str) -> None:
        assert settings.MINIO_BUCKET_PRIVATE is not None
        await asyncio.to_thread(
            self._call_client,
            "delete_object",
            Bucket=settings.MINIO_BUCKET_PRIVATE,
            Key=object_key,
        )

    async def delete_object_quietly(self, object_key: str | None) -> bool:
        if not object_key:
            return True
        try:
            await self.delete_object(object_key)
        except Exception:
            return False
        return True

    async def delete_objects_quietly(self, object_keys: Iterable[str]) -> int:
        failed_count = 0
        for object_key in object_keys:
            if not await self.delete_object_quietly(object_key):
                failed_count += 1
        return failed_count

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
        custom_name: str,
        content_type: str,
    ) -> str:
        ext = mimetypes.guess_extension(content_type) or ""
        return (
            f"{self.build_pet_document_prefix(user_id=user_id, pet_id=pet_id, document_type_id=document_type_id)}"
            f"{custom_name}{ext}"
        )
