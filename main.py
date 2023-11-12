import discord
import os
from dotenv import load_dotenv

import aiohttp
import tempfile
from pdf2image import convert_from_path
import io

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name = "hello", description = "Say hello to the bot")
async def hello(ctx):
    await ctx.respond("Hey!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    for attachment in message.attachments:
        if not attachment.filename.endswith('.pdf'):
            continue

        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as response:
                if response.status != 200:
                    print('Response status is not 200')
                    continue

                data = await response.read()
                with tempfile.NamedTemporaryFile() as temp:
                    temp.write(data)

                    files = []
                    pages = convert_from_path(temp.name)
                    for i, page in enumerate(pages, 1):
                        with io.BytesIO() as stream:
                            print(f'Saving as JPEG and writing to stream... (#{i})')
                            page.save(stream, 'JPEG')
                            stream.seek(0)

                            print(f'Creating File class... (#{i})')
                            filename = f'image-{i}.jpg'
                            file = discord.File(stream, filename)
                            files.append(file)

                            if i % 10 == 0:
                                print('Sending 10 files to channel...')
                                await message.channel.send(files=files, silent=True)
                                print('OK')
                                files = []
                            elif len(pages) == i:
                                print(f'Sending {len(files)} file(s) to channel...')
                                await message.channel.send(files=files, silent=True)
                                print('OK')

bot.run(os.getenv('TOKEN'))
