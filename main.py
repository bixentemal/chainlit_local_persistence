import os.path
import pickle
from typing import Dict, List, Optional

import chainlit as cl
import chainlit.data as cl_data
from chainlit import Message
from chainlit.data.utils import queue_until_user_message
from chainlit.element import Element, ElementDict
from chainlit.socket import persist_user_session
from chainlit.step import StepDict
from chainlit.types import (
    Feedback,
    PageInfo,
    PaginatedResponse,
    Pagination,
    ThreadDict,
    ThreadFilter,
)
from literalai.helper import utc_now

from cl_local_data_layer import ClLocalDataLayer
from local_data_layer import LocalDataLayer


@cl.on_chat_start
async def main():
    await cl.Message("Hello, send me a message!").send()


@cl.on_message
async def handle_message(message: Message):
    # Wait for queue to be flushed
    await cl.sleep(2)
    async with cl.Step(type="tool", name="thinking") as step:
        step.output = "Thinking..."
    await cl.Message("Answer to %s"%(message.content)).send()

@cl.password_auth_callback
def auth_callback(username: str, password: str) -> Optional[cl.User]:
    if (username, password) == ("admin", "admin"):
        return cl.User(identifier="admin")
    else:
        return None


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    # await cl.Message(f"Welcome back to {thread['name']}").send()
    # if "metadata" in thread:
    #     await cl.Message(thread["metadata"], author="metadata", language="json").send()
    # if "tags" in thread:
    #     await cl.Message(thread["tags"], author="tags", language="json").send()
    pass


if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    import chainlit.data as cl_data

    #hardcoded sign key for demo
    os.environ["CHAINLIT_AUTH_SECRET"]="Lg8H744H:mPj2.cMZk9xtp2ko%IEbApq$rh@VLJhuml05aRg?yW^ieD5Wzw81un3"
    history_file = "/tmp/chainlit_hist.json"

    cl_data._data_layer = ClLocalDataLayer(LocalDataLayer.from_file(history_file))
    run_chainlit(__file__)
