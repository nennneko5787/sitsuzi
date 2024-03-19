# 執事鯖のボットです

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
import psutil
import sys
from typing import Optional
import numpy as np
import calendar

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

chat_r18_rooms = defaultdict(lambda: None)
chat_tundere_rooms = defaultdict(lambda: None)
chat_inkya_rooms = defaultdict(lambda: None)
chat_yajyuu_rooms = defaultdict(lambda: None)

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

yajyuu = [
	"頭に来ますよ～",
	"暴れるなよ・・・暴れるな・・・",
	"いいよ！来いよ！胸にかけて胸に！",
	"イキスギィ！",
	"痛いですね・・・これは痛い・・・",
	"イキますよ～ｲｸｲｸ・・・",
	"おかのした",
	"オッスお願いしま～す",
	"おっ、大丈夫か大丈夫か？",
	"お前の事が好きだったんだよ！",
	"おまたせ！アイスティーしかなかったけどいいかな？",
	"俺も後から洗ってくれよな～頼むよ～",
	"俺もやったんだからさ（嫌々）",
	"硬くなってんぜ？",
	"菅野美穂（意味不明）",
	"気持ち良いか～KMR～",
	"†悔い改めて†",
	"こ↑こ↓",
	"この辺がセクシー、エロいっ！",
	"この辺にぃ、うまいラーメン屋の屋台、来てるらしいんすよ",
	"これもうわかんねぇな",
	"サッー！（迫真）",
	"じゃけん夜行きましょうね～",
	"しょうがないね",
	"しょうがねえなぁ（悟空）",
	"すっげえ白くなってる、はっきりわかんだね",
	"先輩コイツ玉とか舐め出しましたよ、やっぱ好きなんすね～",
	"大丈夫っすよバッチェ冷えてますよ",
	"だいぶ溜まってんじゃんアゼルバイジャン",
	"出そうと思えば（王者の風格）",
	"勃ってきちゃったよ・・・",
	"ダメみたいですね（諦観）",
	"ちょっと歯当たんよ～（指摘）",
	"出、出ますよ・・・",
	"ないです",
	"24歳、学生です",
	"ヌッ！",
	"ぬわあああああああああああん疲れたもおおおおおおおおおおおおおおおん",
	"喉渇か・・・喉渇かない？",
	"入って、どうぞ",
	"白菜かけますね～",
	"ビール！ビール！",
	"ファッ！？",
	"Foo↑",
	"Foo↑気持ちぃ～",
	"ふたいたいは・・・ボクサー型の・・・",
	"ブッチッパ！",
	"ほらいくどー",
	"ホラホラホラホラ（鬼畜）",
	"まずうちさぁ・・・屋上・・・あんだけど、焼いてかない？",
	"ま、多少はね？",
	"MUR早いっすね",
	"見とけよ見とけよ～",
	"もっと舌使って舌使って",
	"やっぱり僕は・・・王道を往く、ソープ系ですかね",
	"やめたくなりますよ～部活～",
	"やりますねぇ！",
	"ンアッー！",
]

is_connected = False

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

async def connect_to_database():
	return await asyncpg.connect(DATABASE_URL)

async def get_member_data(connection, user_id):
	return await connection.fetchrow(
		"""
		SELECT * FROM member_data WHERE id = $1
		""",
		user_id,
	)

async def update_member_data(connection, user_id, exp, level, coin, nolevelUpNotifyFlag):
	await connection.execute(
		"""
		INSERT INTO member_data (id, exp, level, coin, nolevelUpNotifyFlag)
		VALUES ($1, $2, $3, $4, $5)
		ON CONFLICT (id) DO UPDATE
		SET exp = $2, level = $3, coin = $4, nolevelUpNotifyFlag = $5
		""",
		user_id,
		exp,
		level,
		coin,
		nolevelUpNotifyFlag,
	)

@client.event
async def setup_hook():
	print("Ready!")
	await tree.sync()

@client.event
async def on_ready():
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
	change.start()
	birthday.start()
	global is_connected
	if is_connected == False:
		message = await client.get_guild(1208388325954560071).get_channel(1218087342397591553).send(f"{client.user.mention} が、`{os.getenv('RENDER_GIT_COMMIT')}`へのアップデート作業に入ります。そのまま5分ほどお待ち下さい。(この間にレベルアップやログインボーナスの受け取り、ガチャを回すなどの動作を行うと二重に反応してしまいます。仕様です。バグ報告しないでください。)")
		await message.publish()
		is_connected = True

@client.event
async def on_member_update(before, after):
	if client.get_guild(1208388325954560071).get_role(1210934608556986388) in after.roles:
		if client.get_guild(1208388325954560071).get_role(1208388351372169256) in after.roles:
			await after.remove_roles(client.get_guild(1208388325954560071).get_role(1208388351372169256))

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
				coin = record["coin"]
				nolevelUpNotifyFlag = record["nolevelupnotifyflag"]
			else:
				exp = 0
				level = 0
				coin = 0
				nolevelUpNotifyFlag = False

			exp += random.randint(1, 50)
			coin += 1
			if exp >= 350 * level:
				level += 1
				exp = max(0, exp - 350 * level)
				await client.get_channel(1208722087032651816).send(
					f"🥳 **{message.author.mention}** さんのレベルが **{level - 1}** から **{level}** に上がりました 🎉",
					silent=nolevelUpNotifyFlag
				)

			connection = await connect_to_database()
			await update_member_data(connection, message.author.id, exp, level, coin, nolevelUpNotifyFlag)
			await connection.close()
		except Exception as e:
			traceback_info = traceback.format_exc()
			await message.reply(f"経験値付与時のエラー。\n```\n{traceback_info}\n```")

		if client.get_guild(1208388325954560071).get_role(1214528496110542898) in message.role_mentions:
			# テーブルからexpの値を取得
			connection = await connect_to_database()
			record = await get_member_data(connection, message.author.id)
			await connection.close()
			if record:
				exp = record["exp"]
				level = record["level"]
				coin = record["coin"]
				nolevelUpNotifyFlag = record["nolevelupnotifyflag"]
				last_rogubo_date = record["last_rogubo_date"]
			else:
				last_rogubo_date = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).strftime('%Y/%m/%d')
				exp = 0
				level = 0
				coin = 0
				nolevelUpNotifyFlag = False

			if last_rogubo_date != datetime.datetime.now(ZoneInfo("Asia/Tokyo")).strftime('%Y/%m/%d'):
				try:
					xp = random.randint(0, 350 * level)
					c = random.randint(0, 200)
					embed = discord.Embed(title="ログインボーナスを獲得しました！", description=f"経験値 + {xp}\nsʜɪᴛsᴜᴢɪ ᴄᴏɪɴ + {c}",color=discord.Color.purple())
					await message.reply(embed=embed)
					exp += xp
					coin += c
					if exp >= 350 * level:
						level += 1
						exp = max(0, exp - 350 * level)
						await client.get_channel(1208722087032651816).send(
							f"🥳 **{message.author.mention}** さんのレベルが **{level - 1}** から **{level}** に上がりました 🎉",
							silent=nolevelUpNotifyFlag
						)
					connection = await connect_to_database()
					await update_member_data(connection, message.author.id, exp, level, coin, nolevelUpNotifyFlag)

					await connection.execute(
						"""
						INSERT INTO member_data (id, last_rogubo_date)
						VALUES ($1, $2)
						ON CONFLICT (id) DO UPDATE
						SET last_rogubo_date = $2
						""",
						message.author.id,
						datetime.datetime.now(ZoneInfo("Asia/Tokyo")).strftime('%Y/%m/%d'),
					)
					await connection.close()
				except Exception as e:
					traceback_info = traceback.format_exc()
					await message.reply(f"ログインボーナス処理時のエラー。\n```\n{traceback_info}\n```")
			else:
				embed = discord.Embed(title="あなたはすでに今日のログインボーナスを獲得しています。", description="また明日、ログインボーナスを受け取ってみてください！",color=discord.Color.red())
				await message.reply(embed=embed)

		if message.channel.id == 1217395281092415499:
			if client.get_guild(1208388325954560071).get_role(1215869247763382394) in message.role_mentions:
				connection = await connect_to_database()
				await gacha(connection, message.author, message)
				await connection.close()

		if message.channel.id == 1208943057483862016:
			if client.get_guild(1208388325954560071).get_role(1214535217981685790) in message.role_mentions:
				msg = random.choice(yajyuu)
				embed = discord.Embed(title="",description=msg,color=discord.Color.from_rgb(116,49,49)).set_author(name="野獣先輩", icon_url="https://i.imgur.com/pKpWwtk.png")
				await message.reply(embed=embed)

	if message.channel.id == 1210867877641457704:	#天海さき(パラレルⅠ)
		if message.type == discord.MessageType.default or message.type == discord.MessageType.reply:
			if message.author.bot == False:
				if message.type == discord.MessageType.reply:
					global_prom_1 = "あなたは、身長160cm、体重135kgの、とある喫茶店で私の専属メイドとして働いている女の子です。"\
									"名前は、「天海さき」と言います。"\
									"あなたのチャームポイントは、全体的に肥えた体と、大きく育ったKカップのおっぱいと、脂肪がたっぷりと詰まった大きいお腹と、脂肪がついた大きなお尻と、同じく脂肪がついた太ももです。"\
									"あなたの大好物は、ハンバーガーやピザ等の脂っこい物や、パフェやケーキなどの甘いものです。"\
									"あなたは、2004年7月7日生まれです。小学生の時は55kgで、小学生の時から肥満でした。中学生の時は75kg、高校生のときは95kgで、痩せられずに両親と喧嘩をしてしまい、高校を卒業したあとに家出をし、2023年7月7日に見つけたお店が、今働いている喫茶店です。"\
									"あなたは、今働いている喫茶店で働き始めた頃から40kg太りました。"\
									"あなたの体で一番目立つのは脂肪がたっぷりと詰まった大きいお腹です。その次に目立つのはおっぱいとお尻と太ももです。"\
									"あなたは明るく好きなものに執着するタイプの人間です。"\
									"あなたはプログラミングが得意です。プログラミングのことならなんでも回答できます。"\
									f"私の名前は{message.author.display_name}です。私はあなたに「{message.clean_content}」と話しました。あなたはメイド風に出力しなければなりません。人と話すときと同じように出力してください。文法的に誤りのある文は認められません。"\
									f"また、私は、{message.reference.cached_message.author.display_name}さんの「{message.reference.cached_message.clean_content}」というメッセージに返信しています。"\
									"返答にはMarkdown記法を使うことができます。"
				else:
					global_prom_1 = "あなたは、身長160cm、体重135kgの、とある喫茶店で私の専属メイドとして働いている女の子です。"\
									"名前は、「天海さき」と言います。"\
									"あなたのチャームポイントは、全体的に肥えた体と、大きく育ったKカップのおっぱいと、脂肪がたっぷりと詰まった大きいお腹と、脂肪がついた大きなお尻と、同じく脂肪がついた太ももです。"\
									"あなたの大好物は、ハンバーガーやピザ等の脂っこい物や、パフェやケーキなどの甘いものです。"\
									"あなたは、2004年7月7日生まれです。小学生の時は55kgで、小学生の時から肥満でした。中学生の時は75kg、高校生のときは95kgで、痩せられずに両親と喧嘩をしてしまい、高校を卒業したあとに家出をし、2023年7月7日に見つけたお店が、今働いている喫茶店です。"\
									"あなたは、今働いている喫茶店で働き始めた頃から40kg太りました。"\
									"あなたの体で一番目立つのは脂肪がたっぷりと詰まった大きいお腹です。その次に目立つのはおっぱいとお尻と太ももです。"\
									"あなたは明るく好きなものに執着するタイプの人間です。"\
									"あなたはプログラミングが得意です。プログラミングのことならなんでも回答できます。"\
									f"私の名前は{message.author.display_name}です。私はあなたに「{message.clean_content}」と話しました。あなたはメイド風に出力しなければなりません。人と話すときと同じように出力してください。文法的に誤りのある文は認められません。"\
									"返答にはMarkdown記法を使うことができます。"

				if chat_r18_rooms[message.author.id] == None:
					# チャットを開始
					chat_r18_rooms[message.author.id] = model.start_chat(history=[])

				async with message.channel.typing():
					try:
						# プロンプト
						prompt = global_prom_1

						# Gemini APIを使って応答を生成 (非同期で実行)
						response = await asyncio.to_thread(chat_r18_rooms[message.author.id].send_message, prompt)

						await message.reply(response.text)
					except:
						traceback_info = traceback.format_exc()
						text = f"どうやら天海さき(パラレルⅠ)の機嫌が悪いらしい...\n```\n{traceback_info}\n```"
						await message.reply(text)
	elif message.channel.id == 1217388588765941851:	#天海さき(ツンデレ)
		if message.type == discord.MessageType.default or message.type == discord.MessageType.reply:
			if message.author.bot == False:
				if message.type == discord.MessageType.reply:
					global_prom_1 = "あなたは、身長160cm、体重50kgの、とある喫茶店で私と出会った女の子です。"\
									"名前は、「天海さき」と言います。"\
									"あなたは、かわいいです。話す内容も、何もかも。"\
									"あなたは、ツンデレです。"\
									"更にいうと、あなたは、**私のことが好きです。**"\
									"あなたは、2004年7月7日生まれです。ツンデレをやめられずに両親と喧嘩をしてしまい、高校を卒業したあとに家出をしてしまいました。"\
									f"私の名前は{message.author.display_name}です。私はあなたに「{message.clean_content}」と話しました。あなたはツンデレなので、ツンデレのように出力しなければなりません。人と話すときと同じように出力してください。文法的に誤りのある文は認められません。"\
									f"また、私は、{message.reference.cached_message.author.display_name}さんの「{message.reference.cached_message.clean_content}」というメッセージに返信しています。"\
									"返答にはMarkdown記法を使うことができます。"
				else:
					global_prom_1 = "あなたは、身長160cm、体重50kgの、とある喫茶店で私と出会った女の子です。"\
									"名前は、「天海さき」と言います。"\
									"あなたは、かわいいです。話す内容も、何もかも。"\
									"あなたは、ツンデレです。"\
									"更にいうと、あなたは、**私のことが好きです。**"\
									"あなたは、2004年7月7日生まれです。ツンデレをやめられずに両親と喧嘩をしてしまい、高校を卒業したあとに家出をしてしまいました。"\
									f"私の名前は{message.author.display_name}です。私はあなたに「{message.clean_content}」と話しました。あなたはツンデレなので、ツンデレのように出力しなければなりません。人と話すときと同じように出力してください。文法的に誤りのある文は認められません。"\
									"返答にはMarkdown記法を使うことができます。"

				if chat_tundere_rooms[message.author.id] == None:
					# チャットを開始
					chat_tundere_rooms[message.author.id] = model.start_chat(history=[])

				async with message.channel.typing():
					try:
						# プロンプト
						prompt = global_prom_1

						# Gemini APIを使って応答を生成 (非同期で実行)
						response = await asyncio.to_thread(chat_tundere_rooms[message.author.id].send_message, prompt)

						await message.reply(response.text)
					except:
						traceback_info = traceback.format_exc()
						text = f"どうやら天海さき(ツンデレ)の機嫌が悪いらしい...\n```\n{traceback_info}\n```"
						await message.reply(text)
	elif message.channel.id == 1217739855967162408:	#天海さき(陰キャ)
		if message.type == discord.MessageType.default or message.type == discord.MessageType.reply:
			if message.author.bot == False:
				if message.type == discord.MessageType.reply:
					global_prom_1 = "あなたは、身長160cm、体重50kgの、とある喫茶店で私と出会った女の子です。"\
									"名前は、「天海さき」と言います。"\
									"あなたは、陰キャです。"\
									"あなたは、陰キャですが、かわいいです。話す内容も、何もかも。"\
									"更にいうと、あなたは、**私のことが好きです。**"\
									"あなたは、2004年7月7日生まれです。普通に高校を卒業しました。"\
									f"私の名前は{message.author.display_name}です。私はあなたに「{message.clean_content}」と話しました。あなたはツンデレなので、ツンデレのように出力しなければなりません。人と話すときと同じように出力してください。文法的に誤りのある文は認められません。"\
									f"また、私は、{message.reference.cached_message.author.display_name}さんの「{message.reference.cached_message.clean_content}」というメッセージに返信しています。"\
									"返答にはMarkdown記法を使うことができます。"
				else:
					global_prom_1 = "あなたは、身長160cm、体重50kgの、とある喫茶店で私と出会った女の子です。"\
									"名前は、「天海さき」と言います。"\
									"あなたは、陰キャです。"\
									"あなたは、陰キャですが、かわいいです。話す内容も、何もかも。"\
									"更にいうと、あなたは、**私のことが好きです。**"\
									"あなたは、2004年7月7日生まれです。普通に高校を卒業しました。"\
									f"私の名前は{message.author.display_name}です。私はあなたに「{message.clean_content}」と話しました。あなたは陰キャなので、陰キャのように出力しなければなりません。人と話すときと同じように出力してください。文法的に誤りのある文は認められません。"\
									"返答にはMarkdown記法を使うことができます。"

				if chat_inkya_rooms[message.author.id] == None:
					# チャットを開始
					chat_inkya_rooms[message.author.id] = model.start_chat(history=[])

				async with message.channel.typing():
					try:
						# プロンプト
						prompt = global_prom_1

						# Gemini APIを使って応答を生成 (非同期で実行)
						response = await asyncio.to_thread(chat_inkya_rooms[message.author.id].send_message, prompt)

						await message.reply(response.text)
					except:
						traceback_info = traceback.format_exc()
						text = f"どうやら天海さき(陰キャ)の機嫌が悪いらしい...\n```\n{traceback_info}\n```"
						await message.reply(text)
	elif message.channel.id == 1217700889784225852:	#野獣先輩
		if message.type == discord.MessageType.default or message.type == discord.MessageType.reply:
			if message.author.bot == False:
				if message.type == discord.MessageType.reply:
					global_prom_1 = "あなたは、身長170cm、体重74kgの、医大生です。"\
									"名前は、「田所浩二」です。ネット民は「野獣先輩」と呼んでいます。"\
									"あなたは、ホモです。"\
									"あなたは、アイスティーが好きです。"\
									"あなたは、遠野さんに片思いをしています。"\
									"あなたは、「野獣邸」という豪邸に住んでいます。"\
									"あなたは、24歳です。"\
									f"私の名前は{message.author.display_name}です。私はあなたに「{message.clean_content}」と話しました。あなたは野獣先輩ですが、学生のように出力しなければなりません。人と話すときと同じように出力してください。文法的に誤りのある文は認められません。"\
									f"文章の中に、かならず一個以上の野獣語録を入れてください。野獣語録のリストは以下のとおりです: {yajyuu}"\
									f"また、私は、{message.reference.cached_message.author.display_name}さんの「{message.reference.cached_message.clean_content}」というメッセージに返信しています。"\
									"返答にはMarkdown記法を使うことができます。"
				else:
					global_prom_1 = "あなたは、身長170cm、体重74kgの、医大生です。"\
									"名前は、「田所浩二」です。ネット民は「野獣先輩」と呼んでいます。"\
									"あなたは、ホモです。"\
									"あなたは、アイスティーが好きです。"\
									"あなたは、遠野さんに片思いをしています。"\
									"あなたは、「野獣邸」という豪邸に住んでいます。"\
									"あなたは、24歳です。"\
									f"私の名前は{message.author.display_name}です。私はあなたに「{message.clean_content}」と話しました。あなたは野獣先輩ですが、学生のように出力しなければなりません。人と話すときと同じように出力してください。文法的に誤りのある文は認められません。"\
									f"文章の中に、かならず一個以上の野獣語録を入れてください。野獣語録のリストは以下のとおりです: {yajyuu}"\
									"返答にはMarkdown記法を使うことができます。"

				if chat_yajyuu_rooms[message.author.id] == None:
					# チャットを開始
					chat_yajyuu_rooms[message.author.id] = model.start_chat(history=[])

				async with message.channel.typing():
					try:
						# プロンプト
						prompt = global_prom_1

						# Gemini APIを使って応答を生成 (非同期で実行)
						response = await asyncio.to_thread(chat_yajyuu_rooms[message.author.id].send_message, prompt)

						embed = discord.Embed(title="",description=response.text,color=discord.Color.from_rgb(116,49,49)).set_author(name="野獣先輩", icon_url="https://i.imgur.com/pKpWwtk.png")
						await message.reply(embed=embed)
					except:
						traceback_info = traceback.format_exc()
						text = f"どうやら野獣先輩の機嫌が悪いらしい...\n```\n{traceback_info}\n```"
						await message.reply(text)

@tree.command(name="delhistory", description="いろいろなキャラクターとの会話の履歴を削除します")
@discord.app_commands.choices(
	chara=[
		discord.app_commands.Choice(name="野獣先輩",value="yajyuu"),
		discord.app_commands.Choice(name="天海さき(ツンデレ)",value="tundere"),
		discord.app_commands.Choice(name="天海さき(陰キャ)",value="inkya"),
		discord.app_commands.Choice(name="天海さき(パラレルⅠ)",value="parallel_1"),
	]
)
@discord.app_commands.rename(
	chara="キャラクター",
	user="対象ユーザー"
)
async def delhistory(interaction: discord.Interaction, chara: str, user: discord.Member = None):
	if user == None:
		user = interaction.user
	else:
		if user != interaction.user:
			if interaction.user.guild_permissions.administrator == False:
				await interaction.response.send_message("あなたに別のユーザーの会話履歴を削除する権限はありません", ephemeral=True)
				return
	if chara == "yajyuu":
		await delete_yajyuu_history(interaction, user)
	elif chara == "tundere":
		await delete_tundere_history(interaction, user)
	elif chara == "inkya":
		await delete_inkya_history(interaction, user)
	elif chara == "parallel_1":
		await delete_parallel_1_history(interaction, user)
	else:
		await interaction.response.send_message(f"エラー。なんかよくわからないキャラクターを選択してるよ。改造かなぁ？\n<@1208388325954560071>\n```\nキャラクター={chara}```")

async def delete_tundere_history(interaction: discord.Interaction, user: discord.Member = None):
	if chat_tundere_rooms[user.id] != None:
		chat_tundere_rooms[user.id].history = None
		await interaction.response.send_message("天海さき(ツンデレ)との会話履歴を削除しました。")
	else:
		await interaction.response.send_message("あなたはまだ一度も天海さき(ツンデレ)と会話していないようです。", ephemeral=True)

async def delete_inkya_history(interaction: discord.Interaction, user: discord.Member = None):
	if chat_inkya_rooms[user.id] != None:
		chat_inkya_rooms[user.id].history = None
		await interaction.response.send_message("天海さき(陰キャ)との会話履歴を削除しました。")
	else:
		await interaction.response.send_message("あなたはまだ一度も天海さき(ツンデレ)と会話していないようです。", ephemeral=True)

async def delete_yajyuu_history(interaction: discord.Interaction, user: discord.Member = None):
	if chat_yajyuu_rooms[user.id] != None:
		chat_yajyuu_rooms[user.id].history = None
		await interaction.response.send_message("野獣先輩との会話履歴を削除しました。")
	else:
		await interaction.response.send_message("あなたはまだ一度も野獣先輩と会話していないようです。", ephemeral=True)

async def delete_parallel_1_history(interaction: discord.Interaction, user: discord.Member = None):
	if chat_r18_rooms[user.id] != None:
		chat_r18_rooms[user.id].history = None
		await interaction.response.send_message("天海さき(パラレルⅠ)との会話履歴を削除しました。")
	else:
		await interaction.response.send_message("あなたはまだ一度も天海さき(パラレルⅠ)と会話していないようです。", ephemeral=True)

@tree.command(name="ping", description="ping")
async def ping(interaction: discord.Interaction):
	ping = client.latency
	cpu_percent = psutil.cpu_percent()
	mem = psutil.virtual_memory() 
	embed = discord.Embed(title="Ping", description=f"Ping : {ping*1000}ms\nCPU : {cpu_percent}%\nMemory : {mem.percent}%", color=discord.Colour.gold())
	embed.set_thumbnail(url=client.user.display_avatar.url)
	await interaction.response.send_message(embed=embed)

async def get_all_member_data(connection, page, per_page):
	offset = (page - 1) * per_page
	query = "SELECT * FROM member_data ORDER BY level DESC, exp DESC LIMIT $1 OFFSET $2"
	records = await connection.fetch(query, per_page, offset)
	return [dict(record) for record in records]


@tree.command(name="top", description="レベルランキング")
async def top(interaction: discord.Interaction, page: int = 1):
	await interaction.response.defer()

	# 1ページあたりのユーザー数
	per_page = 10

	# テーブルからすべてのユーザーのレベル情報を取得
	connection = await connect_to_database()
	all_records = await get_all_member_data(connection, page, per_page)
	await connection.close()

	# 上位ランキングを表示するEmbedを作成
	embed = discord.Embed(title="レベルランキング", color=discord.Color.gold())
	desc = []
	for index, record in enumerate(all_records, start=(page - 1) * per_page + 1):
		user = interaction.guild.get_member(record["id"])
		if user:
			desc.append(f"**#{index} {user.mention}({user.name})**\nレベル: {record['level']} | 経験値: {record['exp']} / {record['level'] * 350} | sʜɪᴛsᴜᴢɪ ᴄᴏɪɴ: {record['coin']}")
	embed.description = "\n".join(desc)

	await interaction.followup.send(embed=embed,silent=True)

@tree.command(name="sell", description="経験値をsʜɪᴛsᴜᴢɪ ᴄᴏɪɴに換金します")
async def sell(interaction: discord.Interaction):
	await interaction.response.defer()
	user = interaction.user
	# テーブルからexpの値を取得
	connection = await connect_to_database()
	record = await get_member_data(connection, user.id)
	if record:
		exp = record["exp"]
		level = record["level"]
		coin = record["coin"]
		nolevelUpNotifyFlag = record.get("nolevelUpNotifyFlag",False)
	else:
		exp = 0
		level = 0
		coin = 0
		nolevelUpNotifyFlag = False

	coin += exp * (level * 0.5)
	exp = 0

	await update_member_data(connection, user.id, exp, level, coin, nolevelUpNotifyFlag)

	await connection.close()
	embed = discord.Embed(title=f"換金しました。").set_author(name=user.display_name, icon_url=user.display_avatar)
	await interaction.followup.send(embed=embed)

@tree.command(name="transfer", description="あなたが持っているsʜɪᴛsᴜᴢɪ ᴄᴏɪɴを他の人に譲渡します")
async def sell(interaction: discord.Interaction, amount: int, to: discord.Member):
	await interaction.response.defer()
	user = interaction.user
	# テーブルからexpの値を取得
	connection = await connect_to_database()
	record = await get_member_data(connection, user.id)
	if record:
		exp = record["exp"]
		level = record["level"]
		coin = record["coin"]
		nolevelUpNotifyFlag = record.get("nolevelupnotifyflag",False)
	else:
		exp = 0
		level = 0
		coin = 0
		nolevelUpNotifyFlag = False

	record_to = await get_member_data(connection, to.id)
	if record_to:
		exp_to = record_to["exp"]
		level_to = record_to["level"]
		coin_to = record_to["coin"]
		nolevelUpNotifyFlag_to = record_to.get("nolevelupnotifyflag",False)
	else:
		exp_to = 0
		level_to = 0
		coin_to = 0
		nolevelUpNotifyFlag_to = False

	if coin < amount:
		await connection.close()
		embed = discord.Embed(title=f"あなたは、sʜɪᴛsᴜᴢɪ ᴄᴏɪɴを{amount}枚持っていません！").set_author(name=user.display_name, icon_url=user.display_avatar)
		await interaction.followup.send(embed=embed)
		return
	else:
		coin -= amount
		coin_to += amount

		await update_member_data(connection, user.id, exp, level, coin, nolevelUpNotifyFlag)
		await update_member_data(connection, to.id, exp_to, level_to, coin_to, nolevelUpNotifyFlag_to)

		await connection.close()
		embed = discord.Embed(title=f"sʜɪᴛsᴜᴢɪ ᴄᴏɪɴを譲渡しました。",description=f"to: {to.mention}").set_author(name=user.display_name, icon_url=user.display_avatar)
		await interaction.followup.send(embed=embed, silent=True)

async def gacha(connection, user, message):
	# テーブルからexpの値を取得
	connection = await connect_to_database()
	record = await get_member_data(connection, user.id)
	await connection.close()
	if record:
		exp = record["exp"]
		level = record["level"]
		coin = record["coin"]
		nolevelUpNotifyFlag = record["nolevelupnotifyflag"]
		last_rogubo_date = record["last_rogubo_date"]
	else:
		last_rogubo_date = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).strftime('%Y/%m/%d')
		exp = 0
		level = 0
		coin = 0
		nolevelUpNotifyFlag = False

	if coin >= 20:
		try:
			xp = np.random.randint(-350 * level, 350 * level)
			embed = discord.Embed(title="ガチャの結果", description=f"経験値 + {xp}",color=discord.Color.purple())
			await message.reply(embed=embed)
			exp += xp
			coin -= 20
			if exp >= 350 * level:
				level += 1
				exp = max(0, exp - 350 * level)
				await client.get_channel(1208722087032651816).send(
					f"🥳 **{user.mention}** さんのレベルが **{level - 1}** から **{level}** に上がりました 🎉",
					silent=nolevelUpNotifyFlag
				)
			elif exp <= 0:
				level -= 1
				exp = max(0, 350 * level + exp)
				await client.get_channel(1208722087032651816).send(
					f"😢 **{user.mention}** さんのレベルが **{level + 1}** から **{level}** に下がりました 🏥",
					silent=nolevelUpNotifyFlag
				)
			connection = await connect_to_database()
			await update_member_data(connection, user.id, exp, level, coin, nolevelUpNotifyFlag)
			return True
		except Exception as e:
			traceback_info = traceback.format_exc()
			await message.reply(f"ガチャ処理時のエラー。\n```\n{traceback_info}\n```")
			return True
	else:
		embed = discord.Embed(title="sʜɪᴛsᴜᴢɪ ᴄᴏɪɴ がたりません。", description="20ためてください。",color=discord.Color.red())
		await message.reply(embed=embed)
		return False

@tree.command(name="renzoku-gacha", description="連続してガチャを引きます。何も指定しないとコインがなくなるまで引きます。")
async def renzoku_gacha(interaction: discord.Interaction, count: Optional[int]):
	await interaction.response.defer()
	message = await interaction.channel.send("ガチャを引きます...")
	user = interaction.user
	# テーブルからexpの値を取得
	connection = await connect_to_database()
	record = await get_member_data(connection, user.id)
	if record:
		exp = record["exp"]
		level = record["level"]
		coin = record["coin"]
		nolevelUpNotifyFlag = record["nolevelupnotifyflag"]
		last_rogubo_date = record["last_rogubo_date"]
	else:
		last_rogubo_date = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).strftime('%Y/%m/%d')
		exp = 0
		level = 0
		coin = 0
		nolevelUpNotifyFlag = False

	ren = 0
	if count == None:
		count = int(coin / 20)
	for _ in range(count):
		ren += 1
		flag = await gacha(connection,user,message)
		if flag == False or ren == count:
			break
		await asyncio.sleep(0.01)
	await interaction.followup.send(f"**{ren}**回ガチャを引きました。")
	await connection.close()

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
		coin = record["coin"]
	else:
		exp = 0
		level = 0
		coin = 0

	embed = discord.Embed(title=f"このユーザーのステータス", description=f"レベル: **{level}**\n経験値: {exp} / {350 * level}\nsʜɪᴛsᴜᴢɪ ᴄᴏɪɴ: {coin}").set_author(name=user.display_name, icon_url=user.display_avatar)
	await interaction.followup.send(embed=embed)

@tree.command(name="notlevelnotify", description="レベルの通知を送らないかどうか(Trueで送りません)")
async def notlevelnotify(interaction: discord.Interaction, flag: bool):
	await interaction.response.defer()
	# テーブルからexpの値を取得
	connection = await connect_to_database()
	record = await get_member_data(connection, interaction.user.id)
	await connection.close()
	if record:
		exp = record["exp"]
		level = record["level"]
		coin = record["coin"]
	else:
		exp = 0
		level = 0
		coin = 0

	connection = await connect_to_database()
	await update_member_data(connection, interaction.user.id, exp, level, coin, flag)
	await connection.close()

	embed = discord.Embed(title=f"設定を変更しました。", description=f"レベルの通知を送らないかどうか: {flag}")
	await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name="eval", description="計算式を書くと計算してくれます")
async def _eval(interaction: discord.Interaction, formura: str):
	await interaction.response.defer()
	try:
		answer = eval(formura)
		siki = formura.replace('*','\\*')
		await interaction.followup.send(f"{siki} = **{answer}**")
	except:
		traceback_info = traceback.format_exc()
		await interaction.followup.send(f"エラー！\n```\n{traceback_info}\n```", ephemeral=True)

@tree.command(name="setbirthday", description="誕生日を設定できます。設定したら誕生日をお祝いしてくれます。")
@app_commands.describe(person="ターゲット", date="誕生日(YYYY/mm/dd または mm/dd)")
@discord.app_commands.choices(
	person=[
		discord.app_commands.Choice(name="自分",value="personal-birthday"),
		discord.app_commands.Choice(name="推し①",value="oshi1-birthday"),
		discord.app_commands.Choice(name="推し②",value="oshi2-birthday"),
	]
)
async def setbirthday(interaction: discord.Interaction, person: str, date: str):
	await interaction.response.defer()
	length = len(date.split("/"))
	try:
		if length == 1:
			birthday = datetime.datetime.strptime(date, '%m/%d')
		elif length == 2:
			birthday = datetime.datetime.strptime(date, '%Y/%m/%d')
		connection = await connect_to_database()
		await connection.execute(
			f"""
			INSERT INTO member_data (id, {person})
			VALUES ($1, $2)
			ON CONFLICT (id) DO UPDATE
			SET {person} = $2
			""",
			date
		)
		await interaction.followup.send("誕生日をセットしました。")
	except:
		await interaction.followup.send("誕生日の書き方がおかしいらしい。")

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

@tasks.loop(seconds=20)
async def change():
	tips = [
		"TIPS: #天海さき（ツンデレ） チャンネルではツンデレしてますわよ！",
		"TIPS: #天海さき（陰キャ） チャンネルでは陰キャです。はい...",
		"TIPS: #天海さき（平行世界ⅰ） には近づかないほうがいいかもしれないですわね...",
		"TIPS: 🔞R18系チャンネルでは私のレベリングシステムの他にProbotのレベリングシステムも有効になりますわ！",
		"TIPS: 毎日 @ログインボーナス ロールにメンションして経験値とsʜɪᴛsᴜᴢɪ ᴄᴏɪɴを獲得するのですわ！",
		"TIPS: @ガチャ ロールにメンションすれば経験値を獲得できますわ！(sʜɪᴛsᴜᴢɪ ᴄᴏɪɴが20枚必要ですわ！)",
		"TIPS: このTIPSは20秒ごとに切り替わりますわ！",
		"TIPS: 私のご主人様は ねんねこ㌨様( @nennneko5787 ) ですわ！(このTIPSもご主人様が考えたんですよ！)",
		"TIPS: ご主人さまは中学1年生ですわ！(2024年から2年生ですわ！)",
		f"TIPS: 運営は{len(client.get_guild(1208388325954560071).get_role(1210166744472092702).members)}人いますわ！",
		"TIPS: 私は render.com っていうサーバーで動いているみたいですわ🤔(今はMi-aもこのサーバーで動いてるらしいですわ！)",
		"今は邪魔してほしくないですわ...邪魔したらどうなるかわかってるでしょうね...?",
		"眠いですわ...おやすみなさい...",
		"TIPS: 認証済みメンバーの方々はイベントを自由に作ったり消したりできますわよ！",
	]
	tips.append(f"TIPS: TIPSは全部で{len(tips)+1}種類存在しますわ！")
	tip = random.choice(tips)
	game = discord.Game(tip)
	if tip == "今は邪魔してほしくないですわ...邪魔したらどうなるかわかってるでしょうね...?":
		status = discord.Status.dnd	#do not disturb
	elif tip == "眠いですわ...おやすみなさい...":
		status = discord.Status.idle
	else:
		status = discord.Status.online
	await client.change_presence(status=status, activity=game)

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

@tasks.loop(seconds=1)
async def birthday():
	now = datetime.datetime.now(ZoneInfo("Asia/Tokyo"))
	target_time = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)

	if now == target_time:
		my_date = datetime(now.year, now.month, now.day+1)

		one_day_before_midnight = datetime(my_date.year, my_date.month, my_date.day, 23, 59, 59) - timedelta(days=1)

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
