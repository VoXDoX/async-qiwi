import ssl
import certifi
from time import localtime, strftime, time
from aiohttp import ClientSession, ClientTimeout
from typing import Dict, Union, Optional

from .exceptions import (
    QiwiAPIError,
    TokenError,
    PhoneError
)


class AsyncQiwi:
    """
    Асинхронный класс для работы с API Qiwi и Qiwi P2P API
    Получить ключ: https://qiwi.com/api
    Подробнее об API: https://developer.qiwi.com/ru/qiwi-wallet-personal

    :param token: ключ авторизации со страницы https://qiwi.com/api. Нужен для работы с аккаунтом.
    :type token: str
    :param secret_key: секретный ключ авторизации со страницы https://qiwi.com/p2p-admin/transfers/api. Нужен для выставления счетов.
    :type secret_key: str
    """
    def __init__(
            self,
            phone: str = None,
            token: str = None,
            secret_key: str = None) -> None:

        if not token and not secret_key:
            raise TokenError(
                "Invalid Token or Secret Key! You can get it here: "
                "https://qiwi.com/api || https://qiwi.com/p2p-admin/transfers/api"
            )

        self._TOKEN_: str = token
        self._SECRET_KEY_: str = secret_key
        self._PHONE_: str = phone
        self._TIMEOUT_ = ClientTimeout(total=5)
        self._BASE_URL_ = "https://edge.qiwi.com/"
        self._SSL_CONTEXT_ = ssl.create_default_context(cafile=certifi.where())

        self.session: ClientSession = ClientSession(
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    @property
    def random_id(self) -> str:
        return str(int(time() * 5))

    async def getBalance(
            self,
            only_balance: bool = True,
            currency: str = 'qw_wallet_rub'
    ) -> Union[float, dict]:
        """
        Возвращает float баланс иль же полные данные об балансе
        :param only_balance: возвращает только один счет Qiwi
        :type only_balance: bool
        :param currency: счет, который нужно показать, по дефолту рубль
        :type currency: str
        :return: возвращает баланс или же массив балансов
        :rtype: Union[float, dict]
        """
        if not self._TOKEN_ and not self._PHONE_:
            raise TokenError(
                "Invalid Token or phone! You can get it here: https://qiwi.com/api"
            )

        self.session.headers["Authorization"] = "Bearer {}".format(self._TOKEN_)
        url = self._BASE_URL_ + "funding-sources/v2/persons/{}/accounts"

        data = await self.__request(
            url=url.format(self._PHONE_)
        )
        account = data['accounts']
        if only_balance:
            balances = [x for x in account if x['alias'] == currency]

            return balances[0]['balance']['amount']

        return account

    async def createBill(
            self,
            amount: Union[float, int],
            lifetime: int = 15,
            currency: str = "RUB",
            comment: Optional[str] = None,
            bill_id: Optional[int] = None
    ) -> Dict:
        """
        Создание P2P счета для оплаты
        :param amount: сумма счета
        :type amount: Union[float, int]
        :param lifetime: время жизни счета (дефолт 15 минут)
        :type lifetime: int
        :param currency: валюта выставленного счета (дефолт рубль)
        :type currency: str
        :param comment: текст комментария (по дефолту нет)
        :type comment: Optional[str]
        :param bill_id: уникальный ID счета
        :type bill_id: Optional[int]
        :return: Dict
        """
        lifetime = strftime(
            "%Y-%m-%dT%H:%M:%S+03:00", localtime(time() + lifetime * 60)
        )
        data = {
            "amount": {
                "currency": currency,
                "value": amount
            },
            "comment": comment or "",
            "expirationDateTime": lifetime,
        }
        self.session.headers["Authorization"] = "Bearer {}".format(self._SECRET_KEY_)
        response = await self.__request(
            url="https://api.qiwi.com/partner/bill/v1/bills/{}".format(bill_id or self.random_id),
            method="PUT",
            json=data
        )

        return response

    async def checkingBill(
            self,
            bill_id: int
    ) -> Dict:
        """
        Проверяем оплачен ли P2P Qiwi счет по его ID
        :param bill_id: ID выставленного счета
        :type bill_id: int
        :return: Dict
        """
        self.session.headers["Authorization"] = "Bearer {}".format(self._SECRET_KEY_)
        response = await self.__request(
            url="https://api.qiwi.com/partner/bill/v1/bills/{}".format(bill_id)
        )
        return response

    async def pay(
        self,
        number: int,
        amount: Union[float, int],
        currency: str = "643",
        comment: Optional[str] = None,
    ) -> dict:
        """
        Перевод денег на другой кошелек Qiwi
        :param number: счет киви, куда делать перевод
        :param amount: cумма перевода
        :param currency: валюта перевода (деволт рубль)
        :param comment: комментарий перевода
        :return: dict
        """
        if not number:
            raise PhoneError(
                "Invalid Number! Please, enter the number to which you want to transfer money."
            )

        elif not amount:
            raise QiwiAPIError(
                "Invalid Amount! Please, enter the amount you want to transfer."
            )

        data = {
            "id": self.random_id,
            "comment": comment or "",
            "fields": {
                "account": number
            },
            "sum": {
                "amount": amount,
                "currency": currency
            },
            "paymentMethod": {"type": "Account", "accountId": currency},
        }

        self.session.headers["Authorization"] = "Bearer {}".format(self._TOKEN_)

        response = await self.__request(
            url="https://edge.qiwi.com/sinap/api/v2/terms/99/payments",
            method="POST",
            json=data,
        )

        return response

    async def __request(
            self,
            url: str,
            method: str = "GET",
            params: dict = None,
            json: dict = None
    ) -> Dict:
        """

        :param method: метод запроса (GET, POST, PUT)
        :type method: str
        :param url: ссылка для запроса QIWI API
        :type url: str
        :param params: параметры запроса
        :type params: dict
        :param json: json-параметры,
        :type json: dict
        :return: Dict
        """
        request = await self.session.request(
            method=method,
            url=url,
            ssl_context=self._SSL_CONTEXT_,
            params=params,
            json=json
        )
        if request.status == 401:
            raise TokenError(
                "Invalid Token! You can get it here: https://qiwi.com/api"
            )
        answer: dict = await request.json()

        if "code" in answer or "errorCode" in answer:
            raise QiwiAPIError(answer)

        return answer
