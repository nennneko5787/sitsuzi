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
	try:
		answer = eval(formura)
		siki = formura.replace('*','\\*')
		await interaction.response.send_message(f"{sik} = **{answer}**")
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

async def url_to_discord_file(url):
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as response:
			if response.status == 200:
				data = await response.read()
				content_type = response.headers.get("Content-Type")
				
				# MIMEタイプから拡張子を取得します
				extension = mimetypes.guess_extension(content_type)
				
				# ファイル名を作成します
				filename = f"file{extension}"
				
				# io.BytesIOを使ってバイトデータをラップします
				file_data = io.BytesIO(data)
				
				return discord.File(file_data, filename=filename)
			else:
				# リクエストが失敗した場合はエラーを処理します
				return None

@client.event
async def on_message(message):
	# 正規表現パターン
	pattern = r"https://www.deviantart.com/(.*)/art/(.*)"
	# マッチング
	matches = re.findall(pattern, message.content)

	if matches:
		button = discord.ui.Button(label="画像を展開",style=discord.ButtonStyle.primary,custom_id=f"unpack,{message.channel.id}|{message.id}")
		view = discord.ui.View()
		view.add_item(button)
		await message.reply(view=view)
		return

	# 正規表現パターン
	pattern = r"https://(?:x\.com|twitter\.com)/(.*)/status/(.*)"
	# マッチング
	matches = re.findall(pattern, message.content)

	if matches:
		button = discord.ui.Button(label="画像を展開",style=discord.ButtonStyle.primary,custom_id=f"unpack,{message.channel.id}|{message.id}")
		view = discord.ui.View()
		view.add_item(button)
		await message.reply(view=view)
		return

@client.event
async def on_interaction(interaction: discord.Interaction):
	try:
		if interaction.data['component_type'] == 2:
			await on_button_click(interaction)
		# elif interaction.data['component_type'] == 3:
			# await on_dropdown(inter)
	except KeyError:
		pass
	
async def on_button_click(interaction: discord.Interaction):
	custom_id, value = interaction.data["custom_id"].split(",")
	print(custom_id)
	print(interaction.user)
	if custom_id == "unpack":
		await interaction.response.defer()
		try:
			channel_id, message_id = value.split("|")

			channel = client.get_channel(int(channel_id))
			message = await channel.fetch_message(int(message_id))

			fileList = []

			# 正規表現パターン
			pattern = r"https://www.deviantart.com/(.*)/art/(.*)"
			# マッチング
			matches = re.findall(pattern, message.content)

			matched = False

			if matches:
				matched = True
				for match in matches:
					# ユーザー名の取得
					username = match[0]
					
					# 作品タイトルの取得
					artwork_title = match[1]
					
					async with aiohttp.ClientSession() as session:
						async with session.get(f"https://backend.deviantart.com/oembed?url=https://www.deviantart.com/{username}/art/{artwork_title}") as response:
							json = await response.json()
							file = await url_to_discord_file(json["url"])
							fileList.append(file)

			# 正規表現パターン
			pattern = r"https://(?:x\.com|twitter\.com)/(.*)/status/(.*)"
			# マッチング
			matches = re.findall(pattern, message.content)

			if matches:
				matched = True
				for match in matches:
					print(match)

					# ユーザー名の取得
					username = match[0]
					
					# 投稿IDの取得
					post_id = match[1]
					
					async with aiohttp.ClientSession() as session:
						async with session.get(f"https://api.vxtwitter.com/{username}/status/{post_id}") as response:
							json = await response.json()
							for f in json["mediaURLs"]:
								fi = await url_to_discord_file(f)
								fileList.append(fi)

			if matched:
				await interaction.followup.send(files=fileList, ephemeral=True)
			else:
				await interaction.followup.send("エラー！", ephemeral=True)
		except Exception as e:
			traceback_info = traceback.format_exc()
			await interaction.followup.send(f"エラー！\n```\n{traceback_info}\n```", ephemeral=True)

@tree.context_menu(name="「画像を展開」ボタンを削除")
async def delete(interaction: discord.Interaction, message: discord.Message):
	button = message.components[0].children[0]
	custom_id, value = button.custom_id.split(",")
	if custom_id == "unpack":
		channel_id, message_id = value.split("|")
		channel = client.get_channel(int(channel_id))
		try:
			msg = await channel.fetch_message(int(message_id))
			if msg.author == interaction.user:
				await message.delete()
				await interaction.response.send_message("削除しました。", ephemeral=True)
			else:
				await interaction.response.send_message("元メッセージの作者ではないので、「画像を展開」ボタンは消せません。", ephemeral=True)
		except:
			await message.delete()
			await interaction.response.send_message("削除しました。", ephemeral=True)
	else:
		await interaction.response.send_message("そのメッセージに「画像を展開」ボタンはないみたいです", ephemeral=True)

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