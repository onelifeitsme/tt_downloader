import logging

import aiohttp
from exceptions import UrlRedirectedToManPage


logger = logging.getLogger(__name__)

headers = {
    "content-type": "application/json; charset=UTF-8",
    "origin": "https://www.tiktok.com",
    "priority": "u=1, i",
    "referer": "https://www.tiktok.com/",
    "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
}


async def fetch(url, session):
    response = await session.get(url=url, headers=headers)
    if response.real_url.name == '404':
        raise UrlRedirectedToManPage('Такого видео не существует')
    response_text = await response.text()
    return response_text


async def get_download_url(response_text: str):
    url_start_index = response_text.find('playAddr":"') + 11
    url = ''
    for letter in response_text[url_start_index:]:
        url += letter
        if 'tt_chain_token' in url:
            break
    return url.replace("\\u002F", "/")


async def download_video(video_url, session):
    try:
        response = await session.get(video_url)
        video_bytes = b''
        while True:
            chunk = await response.content.read(8192)
            if not chunk:
                break
            video_bytes += chunk
        return video_bytes
    except aiohttp.ClientError:
        raise Exception('Не удалось скачать видео')


async def get_video(url, dev=False):
    session = aiohttp.ClientSession()
    try:
        logger.info('')
        logger.info('')
        logger.info('')
        logger.info('Ниже response_text')
        response_text = await fetch(url, session)
        logger.info(response_text)
        logger.info('')
        logger.info('')
        logger.info('Ниже video_url')
        video_url = await get_download_url(response_text)
        logger.info(video_url)
        logger.info('')
        logger.info('')
        logger.info('Ниже video_bytes')
        video_bytes = await download_video(video_url, session)
        logger.info(video_bytes)
        return video_bytes
    except:
        pass
    finally:
        await session.close()
