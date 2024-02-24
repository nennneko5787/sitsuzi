import os
import discord
from discord import app_commands
import aiohttp
from keep_alive import keep_alive
from discord.ext import tasks
import re
import asyncio
import io
from PIL import Image, ImageDraw, ImageFont
import mimetypes
import traceback
from decimal import Decimal

import sys
sys.set_int_max_str_digits(0)

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

@tree.command(name="eval", description="計算式を書くと計算してくれます")
async def ping(interaction: discord.Interaction, formura: str):
	await interaction.response.defer()
	try:
		answer = eval(formura)
		siki = formura.replace('*','\\*')
		await interaction.followup.send(f"{siki} = **{answer}**")
	except:
		traceback_info = traceback.format_exc()
		await interaction.followup.send(f"エラー！\n```\n{traceback_info}\n```", ephemeral=True)

"""
def crop_center(image, width, height):
	# 画像を中央から指定した幅と高さに切り取る関数
	img_width, img_height = image.size
	
	# 画像が指定した幅と高さよりも小さい場合は拡大する
	if img_width < width or img_height < height:
		max_dimension = max(width, height)
		resize_ratio = max_dimension / max(img_width, img_height)
		new_width = int(img_width * resize_ratio)
		new_height = int(img_height * resize_ratio)
		image = image.resize((new_width, new_height), Image.LANCZOS)
	
	# 中央から指定したサイズで切り取る
	left = max(0, (image.width - width) / 2)
	top = max(0, (image.height - height) / 2)
	right = min(image.width, left + width)
	bottom = min(image.height, top + height)
	return image.crop((left, top, right, bottom))


@tree.command(name="smash", description="スマブラ風の画像を生成")
async def ping(interaction: discord.Interaction, name: str, attachment: discord.Attachment):
	await interaction.response.defer()
	print("生成中")
	# 添付ファイルから画像を読み込む
	file_content = await attachment.read()
	image = Image.open(io.BytesIO(file_content))
	image = crop_center(image, 1200, 720)

	# brush_l.png を読み込む
	brush_image = Image.open("brush_l.png")

	# brush_l.png を image 上に合成する
	image.paste(brush_image, (0, 0), brush_image)

	# フォントとサイズを指定する
	font = ImageFont.truetype("NotoSansJP-ExtraBold.ttf", 120)

	# 文字を描画するためのオブジェクトを作成する
	draw = ImageDraw.Draw(image)

	# 文字の描画位置
	text_position = (0, 330)
	# 文字の色
	text_color = (253, 194, 4)
	# 縁取りの色
	outline_color = "black"
	# 角度
	angle = 45

	# 画像を角度だけ回転する
	rotated_image = image.rotate(angle, expand=True)

	# 文字を描画する
	draw = ImageDraw.Draw(rotated_image)
	draw.text(text_position, "参戦!!", fill=text_color, font=font)

	# 画像をバイナリデータに変換する
	img_byte_array = io.BytesIO()
	rotated_image.save(img_byte_array, format="PNG")
	img_byte_array.seek(0)

	# 画像をDiscordのFileオブジェクトとして作成する
	file = discord.File(img_byte_array, filename="output.png")

	print(f"生成完了")
	# メッセージに画像を添付して送信する
	await interaction.followup.send(file=file)
"""

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