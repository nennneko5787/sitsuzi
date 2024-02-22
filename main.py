import os
import discord
from discord import app_commands
import aiohttp
from keep_alive import keep_alive

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

keep_alive()
client.run(token)