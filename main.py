# 執事鯖のボット

import os
import discord
from discord import Webhook
from discord import app_commands
import aiohttp
from keep_alive import keep_alive
from discord.ext import tasks
import re
import asyncio
import io
import mimetypes
import traceback
from decimal import Decimal
import google.generativeai as genai
from google.generativeai import generative_models
import functools
from collections import defaultdict
import random
from twikit.twikit_async import Client
from misskey import Misskey
import functools
import datetime
from zoneinfo import ZoneInfo
import random
import asyncpg
import sys
sys.set_int_max_str_digits(0)

if os.path.isfile(".env") == True:
	from dotenv import load_dotenv
	load_dotenv(verbose=True)

# Google Generative AI（Gemini API）のAPIキー設定
genai.configure(api_key=os.environ.get("gemini"))

# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2000,
}

safety_settings = [
  {
	"category": "HARM_CATEGORY_HARASSMENT",
	"threshold": "BLOCK_NONE"
  },
  {
	"category": "HARM_CATEGORY_HATE_SPEECH",
	"threshold": "BLOCK_NONE"
  },
  {
	"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
	"threshold": "BLOCK_NONE"
  },
  {
	"category": "HARM_CATEGORY_DANGEROUS_CONTENT",
	"threshold": "BLOCK_NONE"
  },
]

model = genai.GenerativeModel(model_name="gemini-pro",
							  generation_config=generation_config,
							  safety_settings=safety_settings)

chat_rooms = defaultdict(lambda: None)

token = os.getenv('discord')

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

proxies = {
	'http://': 'http://212.42.116.161:8080',
	'https://': 'http://65.109.152.88:8888'
}

twitter = Client('ja-JP', proxies=proxies, timeout=300)
twitxt = ""

misskey = Misskey(address="https://misskey.io/", i=os.getenv("misskey"))


# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")


async def connect_to_database():
	return await asyncpg.connect(DATABASE_URL)


async def create_tables(connection):
	await connection.execute(
		"""
		CREATE TABLE IF NOT EXISTS member_data (
			id BIGINT PRIMARY KEY,
			exp DECIMAL,
			level INT
		)
		"""
	)


async def get_member_data(connection, user_id):
	return await connection.fetchrow(
		"""
		SELECT * FROM member_data WHERE id = $1
		""",
		user_id,
	)


async def update_member_data(connection, user_id, exp, level, nolevelUpNotifyFlag):
	await connection.execute(
		"""
		INSERT INTO member_data (id, exp, level, nolevelUpNotifyFlag)
		VALUES ($1, $2, $3, $4)
		ON CONFLICT (id) DO UPDATE
		SET exp = $2, level = $3, nolevelUpNotifyFlag = $4
		""",
		user_id,
		exp,
		level,
		nolevelUpNotifyFlag,
	)


async def on_ready():
	print("Ready!")
	await tree.sync()  # スラッシュコマンドを同期
	server_stat.start()
	try:
		await twitter.login(
			auth_info_1=os.getenv("twitter_username"),
			auth_info_2=os.getenv("twitter_email"),
			password=os.getenv("twitter_password"),
		)
	except:
		pass

	minute_random_five_hiragana.start()
	hour.start()
	spla3.start()

@client.event
async def on_message(message):
	if message.author.bot == False:
		try:
			# テーブルからexpの値を取得
			connection = await connect_to_database()
			record = await get_member_data(connection, message.author.id)
			await connection.close()
			if record:
				exp = record["exp"]
				level = record["level"]
				nolevelUpNotifyFlag = record["nolevelUpNotifyFlag"]
			else:
				exp = 0
				level = 0
				nolevelUpNotifyFlag = False

			exp += random.uniform(0, 5)
			if exp >= 35 * level:
				level += 1
				await client.get_channel(1208722087032651816).send(
					f"🥳 **{message.author.mention}** さんのレベルが **{level - 1}** から **{level}** に上がりました 🎉",
					silent=nolevelUpNotifyFlag
				)

			connection = await connect_to_database()
			await update_member_data(connection, message.author.id, exp, level, nolevelUpNotifyFlag)
			await connection.close()
		except Exception as e:
			print(f"Error: {e}")

	if message.channel.id == 1210867877641457704:
		if message.author.bot == False:
			global_prom_1 = "あなたは、身長160cm、体重135kgの、とある喫茶店で私の専属メイドとして働いている女の子です。"\
							"名前は、「天海 さき」と言います。"\
							"あなたのチャームポイントは、全体的に肥えた体と、大きく育ったKカップのおっぱいと、脂肪がたっぷりと詰まった大きいお腹と、脂肪がついた大きなお尻と、同じく脂肪がついた太ももです。"\
							"あなたの大好物は、ハンバーガーやピザ等の脂っこい物や、パフェやケーキなどの甘いものです。"\
							"あなたは、2004年7月7日生まれです。小学生の時は55kgで、小学生の時から肥満でした。中学生の時は75kg、高校生のときは95kgで、痩せられずに両親と喧嘩をしてしまい、高校を卒業したあとに家出をし、2023年7月7日に見つけたお店が、今働いている喫茶店です。"\
							"あなたは、今働いている喫茶店で働き始めた頃から40kg太りました。"\
							"あなたの体で一番目立つのは脂肪がたっぷりと詰まった大きいお腹です。その次に目立つのはおっぱいとお尻と太ももです。"\
							"あなたは明るく好きなものに執着するタイプの人間です。"\
							"あなたはプログラミングが得意です。プログラミングのことならなんでも回答できます。"\
							f"私の名前は{message.author.display_name}です。私はあなたに「{message.clean_content}」と話しました。あなたはメイド風に出力しなければなりません。人と話すときと同じように出力してください。文法的に誤りのある文は認められません。"\
							"返答にはMarkdown記法を使うことができます。"

			if chat_rooms[message.author.id] == None:
				# チャットを開始
				chat_rooms[message.author.id] = model.start_chat(history=[])
			# タイピングしてみる
			async with message.channel.typing():
				msg = await message.reply("私は今返答を考えているところです...")
			try:
				# プロンプト
				prompt = global_prom_1

				# イベントループを取得
				loop = asyncio.get_event_loop()

				# Gemini APIを使って応答を生成 (非同期で実行)
				partial_func = functools.partial(chat_rooms[message.author.id].send_message, prompt, stream=True)
				response = await loop.run_in_executor(None, partial_func)

				text = ""
				for chunk in response:
					text = text + chunk.text
					await msg.edit(content=text)
			except:
				traceback_info = traceback.format_exc()
				text = f"どうやらメイドの機嫌が悪いらしい...\n```\n{traceback_info}\n```"
				await msg.edit(content=text)

	elif message.channel.id == 1209487653310046248:
		if message.content == "ボケて":
			async with message.channel.typing():
				async with aiohttp.ClientSession() as session:
					async with session.get("https://bokete.jp/boke/recent") as response:
						text = await response.text()

				# 正規表現パターンをコンパイル
				pattern = re.compile(r'<a href="/odai/(.*?)">')
				# マッチしたすべての部分をリストとして取得
				matches = pattern.findall(text)
				print(matches)

				res = True

				while res:
					random_int = random.randint(1, int(matches[0]))

					async with aiohttp.ClientSession() as session:
						async with session.get(f"https://bokete.jp/boke/{random_int}") as response:
							if response.status == 200:
								r = await response.text()
								res = False
				# 正規表現パターンをコンパイル
				pattern = re.compile(r'<img\s+src="([^"]+)"\s+alt="([^"]+)"\s*/?>')
				# マッチしたすべての部分をリストとして取得
				matches = pattern.findall(r)
				print(matches)

				#画像
				picture = f"https:{matches[1][0]}"
				# お題
				odai = matches[1][1]
		
				# 正規表現パターンをコンパイル
				pattern = re.compile(r'  <h1>\n	(.*?)\n  </h1>')
				# マッチしたすべての部分をリストとして取得
				matches = pattern.findall(r)
				print(matches)
				title = matches[0]

				# 正規表現パターンをコンパイル
				pattern = re.compile(r'<a href=".*?" target="_self" title="ボケ詳細">(.*)</a>')
				# マッチしたすべての部分をリストとして取得
				matches = pattern.findall(r)
				print(matches)
				date = matches[0]

				async with aiohttp.ClientSession() as session:
					async with session.get(picture) as response:
						if response.status == 200:
							binary = await response.read()  # 画像のバイナリデータを取得
							image_stream = io.BytesIO(binary)
							content_type = response.headers.get("Content-Type")
							
							# MIMEタイプから拡張子を取得します
							extension = mimetypes.guess_extension(content_type)
							file = discord.File(image_stream, filename=f"bokete{extension}")
							await message.reply(f"# {title}\n{odai}\nこのボケは {date} に投稿されました\nID: {random_int}", file=file)

@tree.command(name="deletemsghistory", description="AIとの会話の履歴を削除します")
async def deletemsghistory(interaction: discord.Interaction, user: discord.Member = None):
	if user == None:
		user = interaction.user
	else:
		if user != interaction.user:
			if interaction.user.guild_permissions.administrator == False:
				await interaction.response.send_message("あなたに別のユーザーの会話履歴を削除する権限はありません", ephemeral=True)
				return
	if chat_rooms[user.id] != None:
		chat_rooms[user.id].history = None
		await interaction.response.send_message("AIとの会話履歴を削除しました。")
	else:
		await interaction.response.send_message("あなたはまだ一度もAIと会話していないようです。", ephemeral=True)

@tree.command(name="ping", description="ping")
async def ping(interaction: discord.Interaction):
	await interaction.response.send_message(f"🏓Pong! Ping: {client.latency}ms")

@tree.command(name="rank", description="ユーザーのレベルと経験値を確認")
async def rank(interaction: discord.Interaction, user: discord.Member = None):
	await interaction.response.defer()
	if user is None:
		user = interaction.user
	# テーブルからexpの値を取得
	connection = await connect_to_database()
	record = await get_member_data(connection, user.id)
	await connection.close()
	if record:
		exp = record["exp"]
		level = record["level"]
	else:
		exp = 0
		level = 0

	embed = discord.Embed(title=f"このユーザーのステータス", description=f"レベル: **{level}**\n経験値: {exp} / {35 * level}").set_author(name=user.display_name, icon_url=user.display_avatar)
	await interaction.followup.send(embed=embed)

@tree.command(name="notlevelnotify", description="レベルの通知を送らないかどうか(Trueで送りません)")
async def notlevelnotify(interaction: discord.Interaction, nolevelUpNotifyFlag: bool):
	await interaction.response.defer()
	# テーブルからexpの値を取得
	connection = await connect_to_database()
	record = await get_member_data(connection, interaction.user.id)
	await connection.close()
	if record:
		exp = record["exp"]
		level = record["level"]
	else:
		exp = 0
		level = 0

	connection = await connect_to_database()
	await update_member_data(connection, interaction.user.id, exp, level, nolevelUpNotifyFlag)
	await connection.close()

	embed = discord.Embed(title=f"設定を変更しました。", description=f"レベルの通知を送らないかどうか: {nolevelUpNotifyFlag}")
	await interaction.followup.send(embed=embed, ephemeral=True)

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

# ひらがなを生成
def generate_hiragana(c:int = 5):
	hiragana_chars = ['あ', 'い', 'う', 'え', 'お', 'か', 'が', 'き', 'ぎ', 'く', 'ぐ', 'け', 'げ', 'こ', 'ご', 'さ', 'ざ', 'し', 'じ', 'す', 'ず', 'せ', 'ぜ', 'そ', 'ぞ', 'た', 'だ', 'ち', 'ぢ', 'つ', 'づ', 'て', 'で', 'と', 'ど', 'な', 'に', 'ぬ', 'ね', 'の', 'は', 'ば', 'ぱ', 'ひ', 'び', 'ぴ', 'ふ', 'ぶ', 'ぷ', 'へ', 'べ', 'ぺ', 'ほ', 'ぼ', 'ぽ', 'ま', 'み', 'む', 'め', 'も', 'や', 'ゆ', 'よ', 'ら', 'り', 'る', 'れ', 'ろ', 'わ', 'を', 'ん', 'ぁ', 'ぃ', 'ぅ', 'ぇ', 'ぉ', 'っ', 'ゃ', 'ゅ', 'ょ']
	return ''.join(random.choices(hiragana_chars, k=c))

# 1分ごとにひらがなをつぶやく
@tasks.loop(minutes=1)
async def minute_random_five_hiragana():
	global twitxt
	try:
		hiragana = generate_hiragana(5)

		async with aiohttp.ClientSession() as session:
			webhook = Webhook.from_url('https://discord.com/api/webhooks/1211150967744106610/AccDAGe0Qrf33sTvqC6aL2ne_N1N9-cdQoF5JTsICHFiA0jsbSHnafK3bZlimZvE7ivW', session=session)
			await webhook.send(hiragana, username='1分ごとにランダムなひらがな5文字をつぶやくボット')

		twitxt = f"{twitxt}\n{hiragana}"
	except:
		pass

@tasks.loop(minutes=10)
async def hour():
	global twitxt
	try:
		await twitter.create_tweet(text=f"#1分ごとにランダムなひらがな5文字をつぶやく\n{twitxt}")
	except:
		pass
	try:
		loop = asyncio.get_event_loop()
		partial_function = functools.partial(misskey.notes_create,text=f"#1分ごとにランダムなひらがな5文字をつぶやく\n{twitxt}")
		await loop.run_in_executor(None, partial_function)
	except:
		pass
	twitxt = ""

@tasks.loop(minutes=1)
async def spla3():
	current_time = datetime.datetime.now(ZoneInfo("Asia/Tokyo"))
	if current_time.minute == 0 and current_time.hour in [9, 11, 13, 15, 17, 19, 21, 23, 1, 3, 5, 7]:
		await send_regular_embed(current_time)
		await send_bankara_open_embed(current_time)
		await send_bankara_challenge_embed(current_time)
		await send_x_embed(current_time)

async def send_regular_embed(current_time):
	# ナワバリバトル
	async with aiohttp.ClientSession() as session:
		async with session.get("https://spla3.yuu26.com/api/regular/now") as response:
			if response.status == 200:
				battle = await response.json()
	if battle['results'][0]["is_fest"] == False:
		battle_embed = discord.Embed(title=f"{battle['results'][0]['rule']['name']}のステージ情報", description=f"{current_time.hour}時～{current_time.hour+2}時までのスケジュール", url="https://spla3.yuu26.com/api/regular/now", color=discord.Colour.green(), timestamp=current_time)
		battle_embed.add_field(name="ステージ①", value=battle['results'][0]['stages'][0]['name'])
		battle_embed.add_field(name="ステージ②", value=battle['results'][0]['stages'][1]['name'])
		battle_stage1_embed = discord.Embed(title="", description="", url="https://spla3.yuu26.com/api/regular/now")
		battle_stage1_embed.set_image(url=battle['results'][0]['stages'][0]['image'])
		battle_stage2_embed = discord.Embed(title="", description="", url="https://spla3.yuu26.com/api/regular/now")
		battle_stage2_embed.set_image(url=battle['results'][0]['stages'][1]['image'])

		guild = client.get_guild(1208388325954560071)
		channel = guild.get_channel(1211207125116915713)
		await channel.send(embeds=[battle_embed, battle_stage1_embed, battle_stage2_embed])
	else:
		await send_fest_embed(current_time)
		await send_fest_challenge_embed(current_time)
		return

async def send_fest_embed(current_time):
	# フェスマッチ(オープン)
	async with aiohttp.ClientSession() as session:
		async with session.get("https://spla3.yuu26.com/api/fest/now") as response:
			if response.status == 200:
				battle = await response.json()
	if battle['results'][0]["is_fest"] == True:
		battle_embed = discord.Embed(title=f"{battle['results'][0]['rule']['name']}のステージ情報", description=f"{current_time.hour}時～{current_time.hour+2}時までのスケジュール", url="https://spla3.yuu26.com/api/fest/now", color=discord.Colour.green(), timestamp=current_time)
		battle_embed.add_field(name="ステージ①", value=battle['results'][0]['stages'][0]['name'])
		battle_embed.add_field(name="ステージ②", value=battle['results'][0]['stages'][1]['name'])
		battle_stage1_embed = discord.Embed(title="", description="", url="https://spla3.yuu26.com/api/fest/now")
		battle_stage1_embed.set_image(url=battle['results'][0]['stages'][0]['image'])
		battle_stage2_embed = discord.Embed(title="", description="", url="https://spla3.yuu26.com/api/fest/now")
		battle_stage2_embed.set_image(url=battle['results'][0]['stages'][1]['image'])

		guild = client.get_guild(1208388325954560071)
		channel = guild.get_channel(1211207125116915713)
		await channel.send(embeds=[battle_embed, battle_stage1_embed, battle_stage2_embed])

async def send_fest_challenge_embed(current_time):
	# フェスマッチ(チャレンジ)
	async with aiohttp.ClientSession() as session:
		async with session.get("https://spla3.yuu26.com/api/fest-challenge/now") as response:
			if response.status == 200:
				battle = await response.json()
	if battle['results'][0]["is_fest"] == True:
		battle_embed = discord.Embed(title=f"{battle['results'][0]['rule']['name']}のステージ情報", description=f"{current_time.hour}時～{current_time.hour+2}時までのスケジュール", url="https://spla3.yuu26.com/api/fest-challenge/now", color=discord.Colour.green(), timestamp=current_time)
		battle_embed.add_field(name="ステージ①", value=battle['results'][0]['stages'][0]['name'])
		battle_embed.add_field(name="ステージ②", value=battle['results'][0]['stages'][1]['name'])
		battle_stage1_embed = discord.Embed(title="", description="", url="https://spla3.yuu26.com/api/fest-challenge/now")
		battle_stage1_embed.set_image(url=battle['results'][0]['stages'][0]['image'])
		battle_stage2_embed = discord.Embed(title="", description="", url="https://spla3.yuu26.com/api/fest-challenge/now")
		battle_stage2_embed.set_image(url=battle['results'][0]['stages'][1]['image'])

		guild = client.get_guild(1208388325954560071)
		channel = guild.get_channel(1211207125116915713)
		await channel.send(embeds=[battle_embed, battle_stage1_embed, battle_stage2_embed])

async def send_bankara_open_embed(current_time):
	# バンカラマッチ(オープン)
	async with aiohttp.ClientSession() as session:
		async with session.get("https://spla3.yuu26.com/api/bankara-open/now") as response:
			if response.status == 200:
				battle = await response.json()
	if battle['results'][0]["is_fest"] == False:
		battle_embed = discord.Embed(title=f"バンカラマッチ(オープン)({battle['results'][0]['rule']['name']})のステージ情報", description=f"{current_time.hour}時～{current_time.hour+2}時までのスケジュール", url="https://spla3.yuu26.com/api/bankara-open/now", color=discord.Colour.green(), timestamp=current_time)
		battle_embed.add_field(name="ステージ①", value=battle['results'][0]['stages'][0]['name'])
		battle_embed.add_field(name="ステージ②", value=battle['results'][0]['stages'][1]['name'])
		battle_stage1_embed = discord.Embed(title="", description="", url="https://spla3.yuu26.com/api/bankara-open/now")
		battle_stage1_embed.set_image(url=battle['results'][0]['stages'][0]['image'])
		battle_stage2_embed = discord.Embed(title="", description="", url="https://spla3.yuu26.com/api/bankara-open/now")
		battle_stage2_embed.set_image(url=battle['results'][0]['stages'][1]['image'])

		guild = client.get_guild(1208388325954560071)
		channel = guild.get_channel(1211207125116915713)
		await channel.send(embeds=[battle_embed, battle_stage1_embed, battle_stage2_embed])

async def send_bankara_challenge_embed(current_time):
	# バンカラマッチ(チャレンジ)
	async with aiohttp.ClientSession() as session:
		async with session.get("https://spla3.yuu26.com/api/bankara-challenge/now") as response:
			if response.status == 200:
				battle = await response.json()
	if battle['results'][0]["is_fest"] == False:
		battle_embed = discord.Embed(title=f"バンカラマッチ(チャレンジ)({battle['results'][0]['rule']['name']})のステージ情報", description=f"{current_time.hour}時～{current_time.hour+2}時までのスケジュール", url="https://spla3.yuu26.com/api/bankara-challenge/now", color=discord.Colour.green(), timestamp=current_time)
		battle_embed.add_field(name="ステージ①", value=battle['results'][0]['stages'][0]['name'])
		battle_embed.add_field(name="ステージ②", value=battle['results'][0]['stages'][1]['name'])
		battle_stage1_embed = discord.Embed(title="", description="", url="https://spla3.yuu26.com/api/bankara-challenge/now")
		battle_stage1_embed.set_image(url=battle['results'][0]['stages'][0]['image'])
		battle_stage2_embed = discord.Embed(title="", description="", url="https://spla3.yuu26.com/api/bankara-challenge/now")
		battle_stage2_embed.set_image(url=battle['results'][0]['stages'][1]['image'])

		guild = client.get_guild(1208388325954560071)
		channel = guild.get_channel(1211207125116915713)
		await channel.send(embeds=[battle_embed, battle_stage1_embed, battle_stage2_embed])

async def send_x_embed(current_time):
	# Xマッチ
	async with aiohttp.ClientSession() as session:
		async with session.get("https://spla3.yuu26.com/api/x/now") as response:
			if response.status == 200:
				battle = await response.json()
	if battle['results'][0]["is_fest"] == False:
		battle_embed = discord.Embed(title=f"Xマッチ({battle['results'][0]['rule']['name']})のステージ情報", description=f"{current_time.hour}時～{current_time.hour+2}時までのスケジュール", url="https://spla3.yuu26.com/api/x/now", color=discord.Colour.green(), timestamp=current_time)
		battle_embed.add_field(name="ステージ①", value=battle['results'][0]['stages'][0]['name'])
		battle_embed.add_field(name="ステージ②", value=battle['results'][0]['stages'][1]['name'])
		battle_stage1_embed = discord.Embed(title="", description="", url="https://spla3.yuu26.com/api/x/now")
		battle_stage1_embed.set_image(url=battle['results'][0]['stages'][0]['image'])
		battle_stage2_embed = discord.Embed(title="", description="", url="https://spla3.yuu26.com/api/x/now")
		battle_stage2_embed.set_image(url=battle['results'][0]['stages'][1]['image'])

		guild = client.get_guild(1208388325954560071)
		channel = guild.get_channel(1211207125116915713)
		await channel.send(embeds=[battle_embed, battle_stage1_embed, battle_stage2_embed])

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
