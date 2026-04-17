from __future__ import annotations

import json
import time
from typing import Callable

from fastapi import Request, Response


async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    payload = {
        "path": request.url.path,
        "method": request.method,
        "status_code": response.status_code,
        "latency_ms": elapsed_ms,
        "request_id": request.headers.get("x-request-id", "na"),
    }
    print(json.dumps(payload))
    return response
