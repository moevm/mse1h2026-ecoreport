import asyncio
from collections import defaultdict
from typing import Any
from urllib.parse import quote


class ReportNotificationHub:
    def __init__(self) -> None:
        self._subscribers: dict[str, set[asyncio.Queue[dict[str, Any]]]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def subscribe(self, user_id: str) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=16)
        async with self._lock:
            self._subscribers[user_id].add(queue)
        return queue

    async def unsubscribe(self, user_id: str, queue: asyncio.Queue[dict[str, Any]]) -> None:
        async with self._lock:
            queues = self._subscribers.get(user_id)
            if queues is None:
                return

            queues.discard(queue)
            if not queues:
                self._subscribers.pop(user_id, None)

    async def publish_report_ready(self, user_id: str, file_name: str) -> None:
        payload = {
            "status": "ready",
            "title": "Отчет готов",
            "file_name": file_name,
            "download_url": f"/download-file/{quote(file_name, safe='')}",
        }

        async with self._lock:
            subscribers = list(self._subscribers.get(user_id, set()))

        for queue in subscribers:
            if queue.full():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass

            queue.put_nowait(payload)


report_notification_hub = ReportNotificationHub()
