import aiofiles
import json
import os


async def all_messages():
    async with aiofiles.open('messages.json', mode='r') as f:
        contents = await f.read()
    messages = json.loads(contents)
    return messages