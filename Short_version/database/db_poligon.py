import asyncio
from db_functions import push_user_info, push_quick_search_parameters


async def main():

    # await push_user_info(123412, "username-dsaf", "Artem", "Sidor", "rus", "thb")

    await push_quick_search_parameters(32142, "FDF", "ASF", ["2023-03-03"])

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())