import dataclasses
import json
import os
import pickle
from enum import Enum

from chainlit.element import Element, ElementDict
from chainlit.step import StepDict
from chainlit.types import (
    Feedback,
    PageInfo,
    PaginatedResponse,
    Pagination,
    ThreadDict,
    ThreadFilter, FeedbackDict,
)
from typing import Dict, List, Optional
import chainlit as cl
from literalai.helper import utc_now
from typing import Self

class SERIALIZER(Enum):
    PICKLE = 1
    JSON = 2


def _determine_serializer(file_path:str):
    extension = file_path.split(".")[-1]
    if extension != "json" and extension != "pickle" :
        raise Exception("unknown extension")
    serializer = None
    if extension == "json":
        serializer = SERIALIZER.JSON
    elif extension == "pickle":
        serializer = SERIALIZER.PICKLE
    return serializer


class LocalDataLayer():

    def __init__(self, thread_history: List = None,
                 storage_root: str = None, serializer: SERIALIZER=SERIALIZER.JSON):
        """ if storage_root is None, thread_history will be transient, thread_will e memory_only"""
        self.thread_history = [] if not thread_history else thread_history
        self.storage_root = storage_root
        self.serializer = serializer

    @classmethod
    def from_file(cls, file_path: str, use_as_persistence: bool = True) -> Self:
        """ if use_as_persistence is False, memory only """
        serializer = _determine_serializer(file_path)
        thread_history = None
        if not os.path.isfile(file_path) or os.stat(file_path).st_size == 0:
            from pathlib import Path
            Path(file_path).touch()
        else:
            if serializer == SERIALIZER.JSON :
                with open(file_path, "r") as f:
                    thread_history = json.load(f)
            elif serializer == SERIALIZER.PICKLE :
                serializer = SERIALIZER.PICKLE
                with open(file_path, "rb") as f:
                    thread_history = pickle.load(f)

        return LocalDataLayer(thread_history,
                              storage_root = file_path if use_as_persistence else None, serializer = serializer)

    async def persist(self):
        if self.storage_root:
            if self.serializer == SERIALIZER.JSON:
                with open(self.storage_root, "w") as out_file:
                    json.dump(self.thread_history, out_file)
            elif self.serializer == SERIALIZER.PICKLE:
                with open(self.storage_root, "wb") as out_file:
                    pickle.dump(self.thread_history, out_file)

    async def get_user(self, identifier: str) -> Optional["PersistedUser"]:
        return cl.PersistedUser(id = "admin", createdAt = '1970-01-01T00:00:00.000Z', identifier = identifier)

    async def create_user(self, user: "User") -> Optional["PersistedUser"]:
        return cl.PersistedUser(id = "admin", createdAt = '1970-01-01T00:00:00.000Z', identifier = user.identifier)

    def _find_step_related_to_feedback_id(self, feedback_id) -> StepDict:
        for t in self.thread_history:
            found = None
            for s in t["steps"]:
                if s["feedback"] and s["feedback"]['id'] == feedback_id:
                    found = s
            if found:
                return found
        return None

    async def delete_feedback(self, feedback_id: str) -> bool:
        step = self._find_step_related_to_feedback_id(feedback_id)
        if step:
            step.update({"feedback": None})
            return True
        return False

    def _find_step(self, stepId) -> StepDict:
        for t in self.thread_history:
            found = None
            for s in t["steps"]:
                if s["id"] == stepId:
                    found = s
            if found:
                return found
        return None

    async def upsert_feedback(self, feedback: Feedback) -> str:
        # retrieve step
        step = self._find_step(feedback.forId)
        if step:
            step.update({"feedback":
                             { 'forId' : feedback.forId,
                               'id' : feedback.id,
                               'comment': feedback.comment,
                               'value' : feedback.value}})
        await self.persist()
        return feedback.id

    async def create_element(self, element: "Element"):
        # we don't store attachments
        pass

    async def get_element(
            self, thread_id: str, element_id: str
    ) -> Optional["ElementDict"]:
        # we don't store attachments
        pass

    async def delete_element(self, element_id: str, thread_id: Optional[str] = None):
        # we don't store attachments
        pass

    #@queue_until_user_message()
    async def create_step(self, step_dict: "StepDict"):
        thread = next(
            (t for t in self.thread_history if t["id"] == step_dict.get("threadId")), None
        )
        if thread:
            thread["steps"].append(step_dict)
        await self.persist()

    #queue_until_user_message()
    async def update_step(self, step_dict: "StepDict"):
        thread = next(
            (t for t in self.thread_history if t["id"] == step_dict.get("threadId")), None
        )
        if thread:
            step = next(
                (s for s in thread["steps"] if s["id"] == step_dict.get("id")), None
            )
            if step :
                if step_dict["name"]:
                    step["name"] = step_dict["name"]
                if step_dict["metadata"]:
                    step["metadata"] = step_dict["metadata"]
                if step_dict["tags"]:
                    step["tags"] =step_dict["tags"]
            else :
                thread["steps"].append(step_dict)
            await self.persist()
            #thread["steps"].remove(step)
            #thread["steps"].append(step_dict)

    async def delete_step(self, step_id: str):
        for t in self.thread_history:
            found = None
            for s in t["steps"]:
                if s["id"] == step_id:
                    found = s
            if found:
                t["steps"].remove(found)
        await self.persist()


    async def get_thread_author(self, thread_id: str) -> str:
        return "admin"

    async def delete_thread(self, thread_id: str):
        idx = -1
        for i in range(len(self.thread_history)):
            if self.thread_history[i]["id"] == thread_id:
                idx = i
                break
        if idx != -1:
            #self.thread_history.remove(idx)
            del self.thread_history[idx]
        await self.persist()

    async def list_threads(
            self, pagination: "Pagination", filters: "ThreadFilter"
    ) -> "PaginatedResponse[ThreadDict]":
        return PaginatedResponse(
            data=[t for t in self.thread_history],
            pageInfo=PageInfo(hasNextPage=False, startCursor=None, endCursor=None),
        )

    async def get_thread(self, thread_id: str) -> "Optional[ThreadDict]":
        thread = next((t for t in self.thread_history if t["id"] == thread_id), None)
        if not thread:
            return None
        thread["steps"] = sorted(thread["steps"], key=lambda x: x["createdAt"])
        return thread

    async def update_thread(
            self,
            thread_id: str,
            name: Optional[str] = None,
            user_id: Optional[str] = None,
            metadata: Optional[Dict] = None,
            tags: Optional[List[str]] = None,
    ):
        thread = next((t for t in self.thread_history if t["id"] == thread_id), None)
        if thread:
            if name:
                thread["name"] = name
            if metadata:
                thread["metadata"] = metadata
            if tags:
                thread["tags"] = tags
        else:
            self.thread_history.append(
                {
                    "id": thread_id,
                    "name": name,
                    "metadata": metadata,
                    "tags": tags,
                    "createdAt": utc_now(),
                    "userId": user_id,
                    "userIdentifier": user_id,
                    "steps": [],
                }
            )
        await self.persist()

    async def build_debug_url(self) -> str:
        return ""