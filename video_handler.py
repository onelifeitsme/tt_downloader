import aiohttp
from exceptions import UrlRedirectedToManPage


async def fetch(url, session):
    response = await session.get(url=url)
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
        response_text = await fetch(url, session)
        video_url = await get_download_url(response_text)
        video_bytes = await download_video(video_url, session)
        return video_bytes
    finally:
        await session.close()
