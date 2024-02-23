import os
import discord
from discord import app_commands
import aiohttp
from keep_alive import keep_alive
from discord.ext import tasks
import re
import asyncio

if os.path.isfile(".env") == True:
	from dotenv import load_dotenv
	load_dotenv(verbose=True)

token = os.getenv('discord')	#Your TOKEN

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# 起動時に動作する処理
@client.event
async def on_ready():
	print("Ready!")
	server_stat.start()
	await tree.sync()	#スラッシュコマンドを同期

@tree.command(name="ping", description="ping")
async def ping(interaction: discord.Interaction):
	await interaction.response.send_message(f"🏓Pong! Ping: {client.latency}ms")
	
@tree.command(name="mcstart", description="Minecraftサーバーを起動します")
async def mcstart(interaction: discord.Interaction):
	await interaction.response.defer()
	url = 'https://panel.fps.ms/api/client/servers/03eaa96e/command'
	headers = {
		'Accept': 'application/json',
		'Content-Type': 'application/json',
		'Authorization': f'Bearer {os.getenv("pterodactyl")}',
	}
	data = {
		"command": "msh start"
	}

	async with aiohttp.ClientSession() as session:
		async with session.post(url, headers=headers, json=data) as response:
			if response.status == 204:
				await interaction.followup.send("起動をリクエストしました。起動まで時間がかかるので、しばらくお待ち下さい...")
			else:
				await interaction.followup.send(f"起動のリクエストに失敗しました。( エラーコード **{response.status}** )")

@tasks.loop(minutes=20)
async def server_stat():
	guild = client.get_guild(1208388325954560071)
	auth = len(guild.get_role(1208388351372169256).members)

	# 参加人数
	channel = client.get_channel(1210425024356286464)
	await channel.edit(name=re.sub(r'(\D*)\d+', f'\g<1>{len(guild.members)}', channel.name))

	await asyncio.sleep(2)

	# メンバー
	channel = client.get_channel(1210425116521930802)
	await channel.edit(name=re.sub(r'(\D*)\d+', f'\g<1>{len([member for member in guild.members if not member.bot])}', channel.name))

	await asyncio.sleep(2)

	# 認証済みメンバー
	channel = client.get_channel(1210425271057121331)
	await channel.edit(name=re.sub(r'(\D*)\d+', f'\g<1>{auth}', channel.name))

	await asyncio.sleep(2)

	# 非認証メンバー
	channel = client.get_channel(1210425314950520912)
	await channel.edit(name=re.sub(r'(\D*)\d+', f'\g<1>{len([member for member in guild.members if not member.bot]) - auth}', channel.name))

	await asyncio.sleep(2)

	# ボット
	channel = client.get_channel(1210425157168926731)
	await channel.edit(name=re.sub(r'(\D*)\d+', f'\g<1>{len([member for member in guild.members if member.bot])}', channel.name))

keep_alive()
client.run(token)