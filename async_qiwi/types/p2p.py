from typing import Dict, Union

from ..exceptions import QiwiAPIError


class Bill:
	"""
	Объект для удобной работы со счетом

    **Аргументы**

    :param response: ответ от серверов киви. Можно просто json.
    :type response: dict
	"""
	def __init__(
			self,
			response: Dict
	) -> None:
		self.data: dict = response
		if "errorCode" in self.data:
			raise QiwiAPIError(
				self.data
			)

		self.bill_id: Union[str, int] = self.data["billId"]
		self.amount: Union[float, int] = self.data["amount"]["value"]
		self.currency: str = self.data["amount"]["currency"]
		self.status: str = self.data["status"]["value"]
		self.status_changed: str = self.data["status"]["changedDateTime"]
		self.creation: str = self.data["creationDateTime"]
		self.expiration: str = self.data["expirationDateTime"]
		self.pay_url: str = self.data["payUrl"]
		self.comment: str = self.data["comment"] if "comment" in self.data else None
