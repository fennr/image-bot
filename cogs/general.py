import sys
import yadisk
import io
import aiohttp
import discord
from discord.ext import commands, tasks

from datetime import datetime
from scripts import config
from scripts import yandex

config = config.read_config()
clear = '\u200b'


class general(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot
        self.image_task.start()

    @commands.command(name="ping")
    async def ping(self, context):
        """
        - Проверка жив ли бот
        """
        embed = discord.Embed(
            color=config["success"]
        )
        embed.add_field(
            name="Pong!",
            value=":ping_pong:",
            inline=True
        )
        embed.set_footer(
            text=f"Pong request by {context.author}"
        )
        await context.send(embed=embed)

    @commands.command(name="start")
    async def start(self, ctx):
        self.image_task.start()
        await ctx.send("Бот запущен")

    @commands.command(name="stop")
    async def stop(self, ctx):
        self.image_task.stop()
        await ctx.send("Бот остановлен")

    @commands.command(name="get_token")
    async def get_token(self, ctx):

        y = yadisk.YaDisk(config["yadisk_id"], config["yadisk_pass"])
        url = y.get_code_url()

        print("Go to the following url: %s" % url)
        code = input("Enter the confirmation code: ")

        try:
            response = y.get_token(code)
        except yadisk.exceptions.BadRequestError:
            print("Bad code")
            sys.exit(1)

        y.token = response.access_token

        if y.check_token():
            print("Sucessfully received token!")
            await ctx.send(f"Токен: {str(y.token)}")
        else:
            print("Something went wrong. Not sure how though...")

    @tasks.loop(seconds=60.0)
    async def image_task(self):
        if yandex.is_good_time(config["time"]):
            print(datetime.now())
            channel = None
            for guild in self.bot.guilds:
                channel = discord.utils.get(guild.text_channels, name=config["channel"])
            images = yandex.get_files(config["root"], config["trash"], config["count"])
            count = 0
            for file in images:
                max_count = len(images) if config["upload"] == 'set' else config["count"]
                if channel is not None:
                    if count < max_count:
                        if yandex.is_readme(file):
                            title = yandex.read_file(file)
                            embed = discord.Embed(title=title, color=config["info"])
                            await channel.send(embed=embed)
                            yandex.move_to_trash(file)
                        else:
                            async with aiohttp.ClientSession() as session:
                                async with session.get(file.file) as resp:
                                    if resp.status != 200:
                                        return await channel.send('Could not download file...')
                                    data = io.BytesIO(await resp.read())
                                    await channel.send(file=discord.File(data, file.name))
                            yandex.move_to_trash(file)
                            count += 1


def setup(bot):
    bot.add_cog(general(bot))
