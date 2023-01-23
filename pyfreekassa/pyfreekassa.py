import hashlib
import pickle
import random
import time
from urllib.parse import urlencode

import aiofiles
import aiohttp


class Nonce:
	"""
	Nonce generators.
	All available methods of storing previously generated nonce are available in \
	Methods subclass
	"""

	class Methods:
		class Method:
			"""DO NOT USE THIS CLASS"""
			def __init__(self, file_extension: str) -> None:
				self.ext = file_extension

		TXT = Method('txt')
		PICKLE = Method('pickle')

	@staticmethod
	def _ensure_path(path: str, method: Methods.Method) -> str:
		if path is None:
			rightpath = './nonce.' + method.ext
		elif not path.endswith(f".{method.ext}"):
			rightpath = path + '.' + method.ext
		else:
			rightpath = path
		return rightpath

	@staticmethod
	async def generate(method: Methods.Method, path: str = None) -> int:
		path = Nonce._ensure_path(path, method)
		if method == Nonce.Methods.TXT:
			async with aiofiles.open(path, 'r+') as f:
				previous_nonce = await f.read()
				if previous_nonce:
					nonce = int(previous_nonce) + 1
				else:
					nonce = 1
				await f.seek(0)
				await f.write(str(nonce))
		elif method == Nonce.Methods.PICKLE:
			async with aiofiles.open(path, 'rb+') as f:
				previous_nonce = pickle.loads(await f.read())
				if previous_nonce:
					nonce = previous_nonce + 1
				else:
					nonce = 1
				await f.seek(0)
				await f.write(pickle.dumps(nonce))
		else:
			raise ValueError("Unknown method")


class OrderId:
	"""Class used to generate order_id for payments"""
	class Methods:
		random_int = 1
		time_hash = 2
		random_int_hash = 3
		custom = 4

	def generate(self, custom_text: str = None) -> str or int:
		"""Generates order_id depending on chosed method

		Args:
			custom_text: Provide this parameter if you want to use custom method. It will be used as order_id
		Returns:
			Generated order_id
		"""
		if self.method == self.Methods.random_int:
			return random.randint(0, 2 ** 32)
		elif self.method == self.Methods.time_hash:
			return hashlib.md5(str(time.time()).encode()).hexdigest()
		elif self.method == self.Methods.random_int_hash:
			return hashlib.md5(str(random.randint(0, 2 ** 32)).encode()).hexdigest()
		elif self.method == self.Methods.custom:
			return custom_text

	def __init__(self, method: int = 1):
		self.method = method


class Currencies:
	"""All currencies available in FreeKassa"""

	class FKwallet:
		RUB = 1
		USD = 2
		EUR = 3

	class Visa:
		RUB = 4
		UAH = 7
		EUR = 11
		USD = 32

	class MasterCard:
		RUB = 8
		UAH = 9

	YOOMONEY = 6
	QIWI = 10
	MIR = 12
	ONLINEBANK = 13
	USDT_ERC20 = 14
	USDT_TRC20 = 15
	BITCOIN_CASH = 16
	BNB = 17
	DASH = 18
	DOGECOIN = 19
	ZCASH = 20
	MONERO = 21
	WAVES = 22
	RIPPLE = 23
	BITCOIN = 24
	LITECOIN = 25
	ETHEREUM = 26
	STEAMPAY = 27
	MEGAFON = 28
	PERFECTMONEY_USD = 33
	SHIBAINU = 34
	QIWI_API = 35
	CARD_RUB_API = 36
	GOOGLEPAY = 37
	APPLEPAY = 38
	TRON = 39
	WEBMONEY_WMZ = 40
	VISA, MASTERCARD_KZT = 41, 41
	SBP = 42


class Configuration:
	"""
	Configuration for the payment system.
	Configured once, can be used for any api requests further.
	Call configure() method to set up the configuration.
	"""
	merchant_id: int
	first_secret: str
	second_secret: str
	wallet_api_key: str

	nonce_generation_method: Nonce.Methods.Method
	nonce_path: str

	@classmethod
	def configure(cls, **kwargs):
		for key, value in kwargs.items():
			setattr(cls, key, value)


class FreekassaApi:
	__payment_form_url = "https://pay.freekassa.ru/"
	__base_api_url = "https://api.freekassa.ru/v1/"

	def generate_signature(self, signature_type: str, request_params: dict = None, order_id: int or str = None) -> str:
		"""Generates signature for payment form

		Args:

			signature_type: Type of signature. Can be "form", "wallet", "api"
			request_params: dict of parameters
			order_id: order_id of payment

		Returns:
			Generated signature str
		"""
		if self.method != OrderId.Methods.custom or order_id is None:
			order_id = OrderId(self.method).generate()
		if signature_type == "form":
			params = [self.config.merchant_id, request_params["payment_amount"], self.config.first_secret, request_params["payment_currency"], order_id]
			params = [str(param) for param in params]
			sign = ':'.join(params)
			return hashlib.md5(sign.encode('utf-8')).hexdigest()
		else:
			keys = list(request_params.keys())
			params = []
			for key in keys:
				params.append(str(request_params[key]))
			separated_params = ':'.join(params)
			return hashlib.md5(separated_params.encode('utf-8')).hexdigest()

	async def get_form_url(self, payment_amount: float, payment_currency: str, suggested_currency: int, phone: str, email: str, lang: str, order_id: str or int = None) -> str:
		"""Generates payment url

		Args:

			payment_amount: payment amount.
			payment_currency: payment currency. Can be RUB, USD, EUR, UAH, KZT
			suggested_currency: currency id. This currency will be suggested to user. User can choose another currency.
			phone: user phone number
			email: user email
			lang: language of payment form. Can be "ru" or "en"
			order_id: Pass this if you use OrderId.Methods.custom

		Returns:
			Generated payment url str
		"""
		if self.method != OrderId.Methods.custom or order_id is None:
			order_id = OrderId(self.method).generate()
		params = {
			"m": self.config.merchant_id,
			"oa": payment_amount,
			"currency": payment_currency,
			"o": order_id,
			"s": self.generate_signature("form"),
			"i": suggested_currency,
			"phone": phone,
			"email": email,
			"lang": lang
		}
		return f"{self.__payment_form_url}?{urlencode(params)}"

	async def get_order_list(
			self,
			order_id: int or str = None,
			payment_id: int or str = None,
			orderstatus: int = None,
			datefrom: str = None,
			dateto: str = None,
			page: int = None
	) -> dict:
		"""Returns order list ❌HAS NOT BEEN TESTED❌

		Args:
			order_id: Order ID
			payment_id: Payment ID
			orderstatus: Order status
			datefrom: Date from
			dateto: Date to
			page: Page number

		Returns:
			dict of orders
		"""
		params = {
			"shopId": self.config.merchant_id,
			"nonce": await Nonce.generate(method=self.config.nonce_generation_method, path=self.config.nonce_path),
			"orderId": order_id,
			"paymentId": payment_id,
			"orderStatus": orderstatus,
			"dateFrom": datefrom,
			"dateTo": dateto,
			"page": page
		}
		params["signature"] = self.generate_signature(signature_type="", request_params=params)
		async with aiohttp.ClientSession() as session:
			async with session.post(self.__base_api_url + 'orders', params=params) as response:
				rjson = await response.json()
				if rjson["type"] == "success":
					return rjson["orders"]
				else:
					raise ValueError("Freekassa API returned error. Try checking args")

	async def create_order(
			self,
			payment_system: int,
			email: str,
			ip: str,
			payment_amount: float,
			payment_currency: str,
			payment_id: int or str = None,
			phone: str = None,
			success_url: str = None,
			failure_url: str = None,
			notification_url: str = None,
	) -> dict:
		"""Creates order ❌HAS NOT BEEN TESTED❌

		Args:
			payment_id: Payment ID
			payment_system: Payment system. Use Currencies class!
			email: User email
			ip: User IP
			payment_amount: Payment amount
			payment_currency: Payment currency. Can be RUB, USD, EUR, UAH, KZT
			phone: User phone number
			success_url: Url to redirect user after successful payment. ASK FREEKASSA SUPPORT TO ENABLE THIS FEATURE
			failure_url: Url to redirect user after failed payment. ASK FREEKASSA SUPPORT TO ENABLE THIS FEATURE
			notification_url: Url to send notification to. ASK FREEKASSA SUPPORT TO ENABLE THIS FEATURE

		Returns:
			dict with orderId, orderHash and location (url)
		"""
		params = {
			"shopId": self.config.merchant_id,
			"nonce": await Nonce.generate(method=self.config.nonce_generation_method, path=self.config.nonce_path),
			"paymentId": payment_id,
			"i": payment_system,
			"email": email,
			"ip": ip,
			"amount": payment_amount,
			"currency": payment_currency,
			"tel": phone,
			"success_url": success_url,
			"failure_url": failure_url,
			"notification_url": notification_url
		}
		params["signature"] = self.generate_signature(signature_type="", request_params=params)
		async with aiohttp.ClientSession() as session:
			async with session.post(self.__base_api_url + 'orders/create', params=params) as response:
				rjson = await response.json()
				if rjson["type"] == "success":
					return {
						"orderId": rjson["orderId"],
						"orderHash": rjson["paymentId"],
						"location": rjson["location"]
					}
				else:
					raise ValueError("Freekassa API returned error. Try checking args")

	async def get_payouts_list(
			self,
			order_id: int or str = None,
			payment_id: int or str = None,
			orderstatus: int = None,
			datefrom: str = None,
			dateto: str = None,
			page: int = None
	) -> dict:
		"""Returns payouts list ❌HAS NOT BEEN TESTED❌

		Args:
			order_id: Order ID
			payment_id: Payment ID
			orderstatus: Order status
			datefrom: Date from
			dateto: Date to
			page: Page number

		Returns:
			dict of payouts
		"""
		params = {
			"shopId": self.config.merchant_id,
			"nonce": await Nonce.generate(method=self.config.nonce_generation_method, path=self.config.nonce_path),
			"orderId": order_id,
			"paymentId": payment_id,
			"orderStatus": orderstatus,
			"dateFrom": datefrom,
			"dateTo": dateto,
			"page": page
		}
		params["signature"] = self.generate_signature(signature_type="", request_params=params)
		async with aiohttp.ClientSession() as session:
			async with session.post(self.__base_api_url + 'withdrawals', params=params) as response:
				rjson = await response.json()
				if rjson["type"] == "success":
					return rjson["orders"]
				else:
					raise ValueError("Freekassa API returned error. Try checking args")

	async def create_payout(
			self,
			payment_system: int,
			account: str,
			payout_amount: float,
			payout_currency: str,
			payment_id: int or str = None,
	) -> dict:
		"""
		Creates payout
		❌HAS NOT BEEN TESTED❌
			payment_id: Payment ID
			payment_system: Payment system. Use Currencies class!
			account: Account to send money to. Can be phone number, card number depending on payment system. If payment system is FKWallet money can be sent only to your own wallet (owner of shop I think)
			payout_amount: Payout amount
			payout_currency: Payout currency. Can be RUB, USD, EUR, UAH, KZT !NOT SURE!
		"""
		params = {
			"shopId": self.config.merchant_id,
			"nonce": await Nonce.generate(method=self.config.nonce_generation_method, path=self.config.nonce_path),
			"paymentId": payment_id,
			"i": payment_system,
			"account": account,
			"amount": payout_amount,
			"currency": payout_currency
		}
		params["signature"] = self.generate_signature(signature_type="", request_params=params)
		async with aiohttp.ClientSession() as session:
			async with session.post(self.__base_api_url + 'withdrawals/create', params=params) as response:
				rjson = await response.json()
				if rjson["type"] == "success":
					return rjson["data"]
				else:
					raise ValueError("Freekassa API returned error. Try checking args")

	async def get_balance(self) -> dict:
		"""Returns shop (merchant) balance."""
		params = {
			"shopId": self.config.merchant_id,
			"nonce": await Nonce.generate(method=self.config.nonce_generation_method, path=self.config.nonce_path),
		}
		params["signature"] = self.generate_signature(signature_type="", request_params=params)
		async with aiohttp.ClientSession() as session:
			async with session.post(self.__base_api_url + 'balance', params=params) as response:
				rjson = await response.json()
				if rjson["type"] == "success":
					return rjson["balance"]
				else:
					raise ValueError("Freekassa API returned error. Try checking args")

	async def get_payment_systems(self) -> dict:
		"""Returns payment systems"""
		params = {
			"shopId": self.config.merchant_id,
			"nonce": await Nonce.generate(method=self.config.nonce_generation_method, path=self.config.nonce_path)
		}
		params["signature"] = self.generate_signature(signature_type="", request_params=params)
		async with aiohttp.ClientSession() as session:
			async with session.post(self.__base_api_url + 'currencies', params=params) as response:
				rjson = await response.json()
				if rjson["type"] == "success":
					return rjson["currencies"]
				else:
					raise ValueError("Freekassa API returned error. Try checking args")

	async def check_payment_system(self, payment_system: int) -> bool:
		"""
		Checks if payment system is available
			payment_system: Payment system to check. You can use Currencies class!
		:return: Boolean [ True - available | False - unavailable ]
		"""
		params = {
			"shopId": self.config.merchant_id,
			"nonce": await Nonce.generate(method=self.config.nonce_generation_method, path=self.config.nonce_path),
		}
		params["signature"] = self.generate_signature(signature_type="", request_params=params)
		async with aiohttp.ClientSession() as session:
			async with session.post(self.__base_api_url + f'currencies/{payment_system}/status', params=params) as response:
				rjson = await response.json()
				if rjson["type"] == "success":
					return True
				else:
					return False

	async def get_available_payment_systems(self):
		"""Returns all payment systems that are currently available for payouts"""
		params = {
			"shopId": self.config.merchant_id,
			"nonce": await Nonce.generate(method=self.config.nonce_generation_method, path=self.config.nonce_path)
		}
		params["signature"] = self.generate_signature(signature_type="", request_params=params)
		async with aiohttp.ClientSession() as session:
			async with session.post(self.__base_api_url + 'withdrawals/currencies', params=params) as response:
				rjson = await response.json()
				if rjson["type"] == "success":
					return rjson["currencies"]
				else:
					raise ValueError("Freekassa API returned error. Try checking args")

	async def get_shops(self):
		"""Returns all your shops"""
		params = {
			"shopId": self.config.merchant_id,
			"nonce": await Nonce.generate(method=self.config.nonce_generation_method, path=self.config.nonce_path)
		}
		params["signature"] = self.generate_signature(signature_type="", request_params=params)
		async with aiohttp.ClientSession() as session:
			async with session.post(self.__base_api_url + 'shops', params=params) as response:
				rjson = await response.json()
				if rjson["type"] == "success":
					return rjson["shops"]
				else:
					raise ValueError("Freekassa API returned error. Try checking args")

	def __init__(
			self,
			config: Configuration,
			wallet_id: int,
			method: int = OrderId.Methods.random_int
	):
		self.config = config
		self.method = method
		self.wallet_id = wallet_id
