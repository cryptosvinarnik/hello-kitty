import asyncio
from concurrent.futures import ThreadPoolExecutor

import aiohttp
from fake_useragent import UserAgent as ua
from loguru import logger
from twocaptcha import TwoCaptcha


try:
    solver = TwoCaptcha(input("TwoCaptcha api key:"))
except KeyboardInterrupt:
    exit()


def solve_captcha():
    return solver.recaptcha(
        sitekey="6LcwIw8TAAAAACP1ysM08EhCgzd6q5JAOUR1a0Go",
        url="https://info.hellokittyfrens.xyz/",
    )


async def register_hello_kitty(worker: str, queue: asyncio.Queue) -> int:
    loop = asyncio.get_running_loop()

    while not queue.empty():
        email = await queue.get()

        logger.info(f"{worker} - waiting for captcha!")

        with ThreadPoolExecutor() as pool:
            resp = await loop.run_in_executor(
                pool,
                lambda: solve_captcha()
            )

        headers = {
            "User-Agent": ua().random,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "cross-site",
            "Referer": "https://info.hellokittyfrens.xyz/",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        }

        params = {
            "u": "62E816C06D88D",
            "f": "4",
            "s": "",
            "c": "0",
            "m": "0",
            "act": "sub",
            "v": "2",
            "or": "0771b5cf2fd799338217053aab20623d",
            "email": email,
            "g-recaptcha-response": resp["code"],
            "jsonp": "true",
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(
                "https://recurforever.activehosted.com/proc.php",
                params=params
            ) as resp:
                if "Thanks" in await resp.text():
                    logger.success(f'{worker} - {email} successfully registered.')
                else:
                    logger.error(f"{worker} - {email} - error")


async def main(emails):
    queue = asyncio.Queue()

    for email in emails:
        queue.put_nowait(email)

    tasks = [asyncio.create_task(register_hello_kitty(
             f"Worker {i}", queue)) for i in range(5)]

    await asyncio.gather(*tasks)
