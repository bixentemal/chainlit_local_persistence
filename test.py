import json
import tempfile
import unittest
from unittest import IsolatedAsyncioTestCase

from chainlit.types import Feedback

from local_data_layer import LocalDataLayer, SERIALIZER


class MyTestCase(IsolatedAsyncioTestCase):

    async def create_LocalDataLayer(self,  storage_root: str = None, serializer: SERIALIZER=SERIALIZER.JSON):
        ldl = LocalDataLayer(storage_root=storage_root, serializer=serializer)
        await ldl.update_thread(
            "thread_1",
            name="Thread 1",
            user_id="admin")
        await ldl.create_step(
            {
                "id": "step_1_1",
                "threadId": "thread_1",
                "name": "test",
                "type": "user_message",
                "output": "Message step1",
            })
        await ldl.update_thread(
            "thread_2",
            name="Thread 2",
            user_id="admin")
        await ldl.create_step(
            {
                "id": "step_2_1",
                "threadId": "thread_2",
                "name": "test",
                "type": "user_message",
                "output": "Message step_2_1",
            })
        await ldl.create_step(
            {
                "id": "step_2_2",
                "threadId": "thread_2",
                "name": "test",
                "type": "user_message",
                "output": "Message step_2_2",
            })
        await ldl.create_step(
            {
                "id": "step_2_3",
                "threadId": "thread_2",
                "name": "test",
                "type": "user_message",
                "output": "Message step_2_3",
            })
        await ldl.delete_step("step_2_2")
        await ldl.update_thread(
            "thread_3",
            name="Thread 3",
            user_id="admin")
        await ldl.create_step(
            {
                "id": "step_3_1",
                "threadId": "thread_3",
                "name": "test",
                "type": "user_message",
                "output": "Message step_3_1",
            })
        await ldl.create_step(
            {
                "id": "step_3_2",
                "threadId": "thread_3",
                "name": "test",
                "type": "user_message",
                "output": "Message step_3_2",
            })
        await ldl.delete_step("step_3_1")
        fb = Feedback(forId="step_3_2", value=0, comment="good")
        await ldl.upsert_feedback(fb)
        return ldl

    async def test(self):
        ldl = await self.create_LocalDataLayer()
        #print(json.dumps(ldl.thread_history, indent=2))
        with open("expected.json", "r") as f:
            expected = [{k: v for k, v in d.items() if k != 'createdAt'} for d in json.load(f) ]
            actual =  [{k: v for k, v in d.items() if k != 'createdAt'} for d in ldl.thread_history ]
            self.assertEqual(expected, actual)


    async def test_save_json(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            ldl = await self.create_LocalDataLayer(tmpdirname + "history.json", SERIALIZER.JSON)
            await ldl.upsert_feedback(Feedback(forId="step_3_2", value=0, comment="bad"))
            await ldl.upsert_feedback(Feedback(forId="step_3_2", value=0, comment="good"))
            ldl2 = LocalDataLayer.from_file(tmpdirname + "history.json")
            expected = [{k: v for k, v in d.items() if k != 'createdAt'} for d in ldl.thread_history ]
            actual =  [{k: v for k, v in d.items() if k != 'createdAt'} for d in ldl2.thread_history ]
            self.assertEqual(expected, actual)

    async def test_save_pickle(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            ldl = await self.create_LocalDataLayer(tmpdirname + "history.pickle", SERIALIZER.PICKLE)
            await ldl.upsert_feedback(Feedback(forId="step_3_2", value=0, comment="bad"))
            await ldl.upsert_feedback(Feedback(forId="step_3_2", value=0, comment="good"))
            ldl2 = LocalDataLayer.from_file(tmpdirname + "history.pickle")
            expected = [{k: v for k, v in d.items() if k != 'createdAt'} for d in ldl.thread_history]
            actual = [{k: v for k, v in d.items() if k != 'createdAt'} for d in ldl2.thread_history]
            self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
