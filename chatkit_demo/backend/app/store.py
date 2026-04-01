import json
from collections import defaultdict
from pathlib import Path

from chatkit.store import NotFoundError, Store
from chatkit.types import Attachment, Page, ThreadItem, ThreadMetadata
from pydantic import TypeAdapter


class MyChatKitStore(Store[dict]):
    def __init__(self):
        self.storage_path = Path(__file__).resolve().parents[1] / "chatkit_store.json"
        self.thread_item_adapter = TypeAdapter(ThreadItem)
        self.threads: dict[str, ThreadMetadata] = {}
        self.items: dict[str, list[ThreadItem]] = defaultdict(list)
        self._load_state()

    async def load_thread(self, thread_id: str, context: dict) -> ThreadMetadata:
        if thread_id not in self.threads:
            raise NotFoundError(f"Thread {thread_id} not found")
        return self.threads[thread_id]

    async def save_thread(self, thread: ThreadMetadata, context: dict) -> None:
        self.threads[thread.id] = thread
        self._dump_state()

    async def load_threads(
        self, limit: int, after: str | None, order: str, context: dict
    ) -> Page[ThreadMetadata]:
        threads = list(self.threads.values())
        return self._paginate(
            threads,
            after,
            limit,
            order,
            sort_key=lambda t: t.created_at,
            cursor_key=lambda t: t.id,
        )

    async def load_thread_items(
        self, thread_id: str, after: str | None, limit: int, order: str, context: dict
    ) -> Page[ThreadItem]:
        items = self.items.get(thread_id, [])
        return self._paginate(
            items,
            after,
            limit,
            order,
            sort_key=lambda i: i.created_at,
            cursor_key=lambda i: i.id,
        )

    async def add_thread_item(
        self, thread_id: str, item: ThreadItem, context: dict
    ) -> None:
        self.items[thread_id].append(item)
        self._dump_state()

    async def save_item(self, thread_id: str, item: ThreadItem, context: dict) -> None:
        items = self.items[thread_id]
        for idx, existing in enumerate(items):
            if existing.id == item.id:
                items[idx] = item
                self._dump_state()
                return
        items.append(item)
        self._dump_state()

    async def load_item(
        self, thread_id: str, item_id: str, context: dict
    ) -> ThreadItem:
        for item in self.items.get(thread_id, []):
            if item.id == item_id:
                return item
        raise NotFoundError(f"Item {item_id} not found in thread {thread_id}")

    async def delete_thread(self, thread_id: str, context: dict) -> None:
        self.threads.pop(thread_id, None)
        self.items.pop(thread_id, None)
        self._dump_state()

    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: dict
    ) -> None:
        self.items[thread_id] = [
            item for item in self.items.get(thread_id, []) if item.id != item_id
        ]
        self._dump_state()

    def _paginate(
        self,
        rows: list,
        after: str | None,
        limit: int,
        order: str,
        sort_key,
        cursor_key,
    ):
        sorted_rows = sorted(rows, key=sort_key, reverse=order == "desc")
        start = 0
        if after:
            for idx, row in enumerate(sorted_rows):
                if cursor_key(row) == after:
                    start = idx + 1
                    break
        data = sorted_rows[start : start + limit]
        has_more = start + limit < len(sorted_rows)
        next_after = cursor_key(data[-1]) if has_more and data else None
        return Page(data=data, has_more=has_more, after=next_after)

    def _load_state(self) -> None:
        if not self.storage_path.exists():
            return

        with self.storage_path.open() as storage_file:
            payload = json.load(storage_file)

        self.threads = {
            thread["id"]: ThreadMetadata.model_validate(thread)
            for thread in payload.get("threads", [])
        }
        self.items = defaultdict(
            list,
            {
                thread_id: [
                    self.thread_item_adapter.validate_python(item)
                    for item in thread_items
                ]
                for thread_id, thread_items in payload.get("items", {}).items()
            },
        )

    def _dump_state(self) -> None:
        payload = {
            "threads": [
                thread.model_dump(mode="json") for thread in self.threads.values()
            ],
            "items": {
                thread_id: [
                    self.thread_item_adapter.dump_python(item, mode="json")
                    for item in thread_items
                ]
                for thread_id, thread_items in self.items.items()
            },
        }
        with self.storage_path.open("w", encoding="utf-8") as storage_file:
            json.dump(payload, storage_file, indent=2)

    async def save_attachment(self, attachment: Attachment, context: dict) -> None:
        raise NotImplementedError()

    async def load_attachment(self, attachment_id: str, context: dict) -> Attachment:
        raise NotImplementedError()

    async def delete_attachment(self, attachment_id: str, context: dict) -> None:
        raise NotImplementedError()
