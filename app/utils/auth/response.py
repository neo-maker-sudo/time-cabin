import json
import typing
from fastapi import Response
from starlette.background import BackgroundTask


class QrcodeResponse(Response):
    media_type = "image/png"
    headers: dict = {
        "Content-Type": "image/png",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }

    def __init__(
        self,
        content: typing.Any,
        status_code: int = 200,
        background: typing.Optional[BackgroundTask] = None,
    ) -> None:
        super().__init__(content, status_code, self.headers, self.media_type, background)

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")