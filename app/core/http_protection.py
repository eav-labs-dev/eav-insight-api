"""Application-level request throttling and body-size protection."""

from __future__ import annotations

import json
import threading
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from starlette.types import Message, Receive, Scope, Send

from app.schemas.error import build_error_response

ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]
AUTH_PATHS = {"/api/v1/auth/register", "/api/v1/auth/token"}
HEALTH_PATHS = {"/api/v1/health"}
WINDOW_SECONDS = 60
STALE_BUCKET_THRESHOLD = 10_000
SECURITY_HEADERS = [
    (b"x-content-type-options", b"nosniff"),
    (b"x-frame-options", b"DENY"),
    (b"referrer-policy", b"no-referrer"),
    (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
]


@dataclass(frozen=True)
class _Window:
    minute: int
    count: int


class HttpProtectionMiddleware:
    """Protect one API process with fixed-window client limits and bounded bodies.

    The production MVP runs one process. A shared backing store should replace this
    process-local state before the application is horizontally scaled.
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        api_limit: int,
        auth_limit: int,
        max_body_bytes: int,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.app = app
        self.api_limit = api_limit
        self.auth_limit = auth_limit
        self.max_body_bytes = max_body_bytes
        self.clock = clock
        self._windows: dict[tuple[str, str], _Window] = {}
        self._lock = threading.Lock()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def secure_send(message: Message) -> None:
            if message["type"] == "http.response.start":
                message.setdefault("headers", []).extend(SECURITY_HEADERS)
            await send(message)

        path = str(scope.get("path", ""))
        if not path.startswith("/api/") or path in HEALTH_PATHS:
            await self.app(scope, receive, secure_send)
            return

        content_length = self._content_length(scope)
        if content_length is not None and content_length > self.max_body_bytes:
            await self._send_error(
                secure_send,
                status_code=413,
                code="request_too_large",
                message="Request body exceeds the configured limit.",
                headers=[],
            )
            return

        messages: list[Message] = []
        received_bytes = 0
        while True:
            message = await receive()
            messages.append(message)
            if message["type"] != "http.request":
                break
            received_bytes += len(message.get("body", b""))
            if received_bytes > self.max_body_bytes:
                await self._send_error(
                    secure_send,
                    status_code=413,
                    code="request_too_large",
                    message="Request body exceeds the configured limit.",
                    headers=[],
                )
                return
            if not message.get("more_body", False):
                break

        limit_name = "auth" if path in AUTH_PATHS else "api"
        limit = self.auth_limit if limit_name == "auth" else self.api_limit
        client = scope.get("client")
        client_host = str(client[0]) if client else "unknown"
        identity = (
            self._auth_identity(client_host, messages)
            if limit_name == "auth"
            else client_host
        )
        allowed, remaining, retry_after = self._consume((limit_name, identity), limit)

        rate_headers = [
            (b"x-ratelimit-limit", str(limit).encode()),
            (b"x-ratelimit-remaining", str(remaining).encode()),
        ]
        if not allowed:
            await self._send_error(
                secure_send,
                status_code=429,
                code="rate_limit_exceeded",
                message="Too many requests. Retry after the current rate-limit window.",
                headers=[*rate_headers, (b"retry-after", str(retry_after).encode())],
            )
            return

        async def replay_receive() -> Message:
            if messages:
                return messages.pop(0)
            return {"type": "http.request", "body": b"", "more_body": False}

        async def add_rate_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                message.setdefault("headers", []).extend(rate_headers)
            await secure_send(message)

        await self.app(scope, replay_receive, add_rate_headers)

    def _auth_identity(self, client_host: str, messages: list[Message]) -> str:
        body = b"".join(
            message.get("body", b"")
            for message in messages
            if message["type"] == "http.request"
        )
        try:
            payload = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return client_host
        email = payload.get("email") if isinstance(payload, dict) else None
        if not isinstance(email, str) or not email.strip():
            return client_host
        return f"{client_host}:{email.strip().casefold()}"

    def _consume(self, key: tuple[str, str], limit: int) -> tuple[bool, int, int]:
        now = int(self.clock())
        minute = now // WINDOW_SECONDS
        with self._lock:
            previous = self._windows.get(key)
            window = (
                _Window(minute, 1)
                if previous is None or previous.minute != minute
                else _Window(minute, previous.count + 1)
            )
            self._windows[key] = window
            if len(self._windows) > STALE_BUCKET_THRESHOLD:
                self._windows = {
                    bucket_key: bucket
                    for bucket_key, bucket in self._windows.items()
                    if bucket.minute >= minute
                }

        remaining = max(0, limit - window.count)
        retry_after = WINDOW_SECONDS - (now % WINDOW_SECONDS)
        return window.count <= limit, remaining, retry_after

    def _content_length(self, scope: Scope) -> int | None:
        for name, value in scope.get("headers", []):
            if name.lower() == b"content-length":
                try:
                    return int(value)
                except ValueError:
                    return None
        return None

    async def _send_error(
        self,
        send: Send,
        *,
        status_code: int,
        code: str,
        message: str,
        headers: list[tuple[bytes, bytes]],
    ) -> None:
        body = json.dumps(build_error_response(code=code, message=message)).encode()
        response_headers = [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode()),
            *headers,
        ]
        await send(
            {"type": "http.response.start", "status": status_code, "headers": response_headers}
        )
        await send({"type": "http.response.body", "body": body})
