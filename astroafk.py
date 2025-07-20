import asyncio
import datetime
import time

from telethon import types
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest

from .. import loader, utils


class AstroAfkMod(loader.Module):
	"""Упрощенный модуль для смены ника при уходе в АФК режим!"""

	async def client_ready(self, client, db):
		self._me = await client.get_me()

	strings = {
		"name": "AstroAFK",
		"lname": "| afk.",
		"bt_off_afk": "🚫 <b>АФК</b> режим <b>отключен</b>!",
	}

	def __init__(self):
		self.config = loader.ModuleConfig(
			loader.ConfigValue(
				"prefix",
				"| afk.",
				doc=lambda: "Префикс, который будет добавляться к вашему имени во время входа в АФК"
			),
		)

	@loader.command()
	async def goafk(self, message):
		""" <reason/empty>- войти в АФК режим"""

		reason = utils.get_args_raw(message)
		if not reason:
			self._db.set(__name__, "reason", "­")
		else:
			self._db.set(__name__, "reason", reason)

		user_id = self._tg_id
		user = await self._client(GetFullUserRequest(user_id))
		
		# Сохраняем оригинальное имя
		original_name = user.users[0].first_name
		original_last_name = user.users[0].last_name or ""
		
		self._db.set(__name__, "afk", True)
		self._db.set(__name__, "gone", time.time())
		self._db.set(__name__, "original_name", original_name)
		self._db.set(__name__, "original_last_name", original_last_name)

		# Меняем имя, добавляя префикс
		prefix = self.config["prefix"]
		new_name = f"{original_name} {prefix}"
		
		await message.client(UpdateProfileRequest(first_name=new_name))

		m = await utils.answer(message, "<emoji document_id=5188391205909569136>✅</emoji> <b>АФК</b> режим был успешно <b>включен</b>!")
		await asyncio.sleep(5)
		await m.delete()

	@loader.command()
	async def ungoafk(self, message):
		"""- выйти из режима АФК"""

		self._db.set(__name__, "afk", False)
		self._db.set(__name__, "gone", None)
		
		# Восстанавливаем оригинальное имя
		original_name = self._db.get(__name__, "original_name")
		original_last_name = self._db.get(__name__, "original_last_name")
		
		if original_name:
			await message.client(UpdateProfileRequest(
				first_name=original_name,
				last_name=original_last_name
			))

		m = await utils.answer(message, "<emoji document_id=5465665476971471368>❌</emoji> <b>АФК</b> режим был успешно <b>выключен</b>!")
		await asyncio.sleep(5)
		await m.delete()
	
	def get_afk(self):
		return self._db.get(__name__, "afk", False)