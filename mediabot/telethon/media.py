"""Download and message replace logic."""
from telethon import events

from mediabot import log, get_peer_information
from mediabot.telethon import bot
from mediabot.download import (
    handle_reddit_web_url,
    download_media,
    Info,
)
from mediabot.config import config
from mediabot.backup import backup_file
from mediabot.link_handling import (
    info_from_imgur,
)


@bot.on(events.NewMessage(pattern='.*reddit\.com.*'))
async def replace_reddit_post_link(event):
    """Replace a reddit link with the actual media of the reddit link."""
    try:
        url = event.message.message
        info, media = handle_reddit_web_url(url)
        if info is None or media is None:
            return
        await handle_file_backup(event, info, media)
        await handle_file_upload(event, info, media)

    except Exception as e:
        log(f"Got exception: {e}")
        pass


@bot.on(events.NewMessage(pattern='.*imgur\.com.*'))
async def replace_imgur_link(event):
    """Handle imgur links."""
    try:
        text = event.message.message
        info = Info()

        log(f'Got imgur link: {text}')
        splitted = text.split('\n')
        if len(splitted) == 1:
            info_from_imgur(info, splitted[0])
        elif len(splitted) == 2:
            info.title = splitted[0]
            info_from_imgur(info, splitted[1])
        elif len(splitted) > 2:
            return

        info, media = download_media(info)
        await handle_file_upload(event, info, media)
    except Exception as e:
        print(e)


async def handle_file_upload(event, info, media):
    """Telethon file upload related logic."""
    log("Handle telethon stuff:")
    log(f"--- Uploading: {info.title}")
    file_handle = await bot.upload_file(
        media,
        file_name=f"{info.title}.{info.type}"
    )

    log("--- Sending")
    me = await bot.get_me()
    # Send the file to the chat and replace the message
    # if the message was send by yourself
    if event.message.from_id == me.id:
        log("--- Sending to chat")
        await bot.send_file(
            event.message.to_id,
            file=file_handle,
            caption=info.title,
        )

        log("--- Deleting old message")
        await event.message.delete()

    # Send the file to a meme chat if it's specified
    chat_id, chat_type = get_peer_information(event.message.to_id)
    meme_chat_id = config['bot']['meme_chat_id']
    if meme_chat_id != '' and meme_chat_id != chat_id:
        log("--- Sending to meme chat")
        await bot.send_file(
            meme_chat_id,
            file=file_handle,
            caption=info.title,
        )


async def handle_file_backup(event, info, media):
    """Backup the file to the disk, if config says so."""
    if config['bot']['backup']:
        log("Backing up media to disk")
        await backup_file(bot, event.message.from_id, info, media)
