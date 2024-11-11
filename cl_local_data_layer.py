import json
import os
import pickle
from enum import Enum

import chainlit.data as cl_data
from chainlit.data.utils import queue_until_user_message
from chainlit.element import Element, ElementDict
from chainlit.server import delete_feedback, delete_thread
from chainlit.step import StepDict
from chainlit.types import (
    Feedback,
    PageInfo,
    PaginatedResponse,
    Pagination,
    ThreadDict,
    ThreadFilter,
)
from typing import Dict, List, Optional
import chainlit as cl
from literalai.helper import utc_now

from local_data_layer import LocalDataLayer


class SERIALIZER(Enum):
    PICKLE = 1
    JSON = 2


class ClLocalDataLayer(cl_data.BaseDataLayer):

    def __init__(self, ldl: LocalDataLayer):
        self.ldl = ldl

    @classmethod
    def from_file(cls, file_path: str, use_as_persistence: bool = True):
        ldl = LocalDataLayer.from_file(file_path, use_as_persistence=use_as_persistence)
        return ClLocalDataLayer(ldl)

    async def get_user(self, identifier: str) -> Optional["PersistedUser"]:
        return await self.ldl.get_user(identifier)

    async def create_user(self, user: "User") -> Optional["PersistedUser"]:
        return await self.ldl.create_user(user)

    async def delete_feedback(self, feedback_id: str) -> bool:
        return await self.ldl.delete_feedback(feedback_id)

    async def upsert_feedback(self, feedback: Feedback) -> str:
        return await self.ldl.upsert_feedback(feedback)

    @queue_until_user_message()
    async def create_element(self, element: "Element"):
        return await self.ldl.create_element(element)

    async def get_element(
            self, thread_id: str, element_id: str
    ) -> Optional["ElementDict"]:
        return await self.ldl.get_element(thread_id, element_id)

    @queue_until_user_message()
    async def delete_element(self, element_id: str, thread_id: Optional[str] = None):
        return await self.ldl.delete_element(element_id, thread_id)

    @queue_until_user_message()
    async def create_step(self, step_dict: "StepDict"):
       return await self.ldl.create_step(step_dict)

    @queue_until_user_message()
    async def update_step(self, step_dict: "StepDict"):
        return await self.ldl.update_step(step_dict)

    @queue_until_user_message()
    async def delete_step(self, step_id: str):
        return await self.ldl.delete_step(step_id)

    async def get_thread_author(self, thread_id: str) -> str:
        return await self.ldl.get_thread_author(thread_id)

    async def delete_thread(self, thread_id: str):
        await  self.ldl.delete_thread(thread_id)

    async def list_threads(
            self, pagination: "Pagination", filters: "ThreadFilter"
    ) -> "PaginatedResponse[ThreadDict]":
        return await self.ldl.list_threads(pagination, filters)

    async def get_thread(self, thread_id: str) -> "Optional[ThreadDict]":
        return await self.ldl.get_thread(thread_id)

    async def update_thread(
            self,
            thread_id: str,
            name: Optional[str] = None,
            user_id: Optional[str] = None,
            metadata: Optional[Dict] = None,
            tags: Optional[List[str]] = None,
    ):
        await self.ldl.update_thread(thread_id, name=name,
                                     user_id=user_id, metadata=metadata, tags=tags)

    async def build_debug_url(self) -> str:
        return await self.ldl.build_debug_url()