import ssl
import certifi
from aiohttp import ClientSession, ClientTimeout
from typing import Dict, Union

from .exceptions import ApiError, WrongToken, PermError


class AsyncQiwi:
    """
    Асинхронный класс для работы с API Qiwi
    Получить ключ: https://qiwi.com/api
    Подробнее об API: https://developer.qiwi.com/ru/qiwi-wallet-personal

    :param token: (Ключ доступа к api)
    :type token: str
    """
    def __init__(self, token: str):
        self._TOKEN_ = token
        self._TIMEOUT_ = ClientTimeout(total=5)
        self._BASE_URL = "https://edge.qiwi.com/"
        self._SSL_CONTEXT_ = ssl.create_default_context(cafile=certifi.where())

    async def getProfile(self,
                         verify_info: bool = True,
                         contract_info: bool = True,
                         user_info: bool = True) -> Dict:
        """
        Получение полных данных об профиле киви
        :param verify_info: Информация об авторизации
        :type verify_info: bool
        :param contract_info: Информация о кошельке
        :type contract_info: bool
        :param user_info: Прочие данные
        :type user_info: bool
        :return: Dict
        """
        url = "person-profile/v1/profile/current"
        params = {
            'authInfoEnabled': "true" if verify_info else "false",
            'contractInfoEnabled': "true" if contract_info else "false",
            'userInfoEnabled': "true" if user_info else "false"
        }

        return await self.__request(path=url, params=params)

    async def getBalance(self,
                         only_balance: bool = True,
                         currency: str = 'qw_wallet_rub') -> Union[float, dict]:
        """
        Возвращает float баланс иль же полные данные об балансе
        :param only_balance: bool
        :param currency: str
        :return: Union[float, dict]
        """
        profile = await self.getProfile(
            contract_info=False,
            user_info=False
        )
        number = profile['authInfo']['personId']
        url = "funding-sources/v2/persons/{}/accounts"

        data = await self.__request(path=url.format(number))
        account = data['accounts']
        if only_balance:
            balances = [x for x in account if x['alias'] == currency]

            return balances[0]['balance']['amount']

        return account

    async def getIndentification(self) -> Dict:
        """
        Получение данных о верификации Qiwi-кошелька
        :return: Dict {
                    'id': None,
                    'firstName': None,
                    'middleName': None,
                    'lastName': None,
                    'birthDate': None,
                    'passport': None,
                    'inn': None,
                    'snils': None,
                    'oms': None,
                    'type': 'ANONYMOUS
                    }
        """
        profile = await self.getProfile(
            contract_info=False,
            user_info=False
        )
        number = profile['authInfo']['personId']
        url = "identification/v1/persons/{}/identification"

        return await self.__request(path=url.format(number))

    async def __request(self,
                        path: str,
                        method: str = "GET",
                        params: dict = None,
                        data: dict = None) -> Dict:
        """
        Создает запрос к API Qiwi с готовыми параметрами и ссылками
        :param path: str (патч к основной ссылке)
        :param method: str (метод запроса)
        :param params: dict (параметры запроса)
        :param data: dict (данные запроса)
        :return: Dict
        """
        url = self._BASE_URL + path
        headers = {
            'Accept': 'application/json',
            'authorization': 'Bearer {}'.format(self._TOKEN_)
        }

        async with ClientSession() as session:
            async with session.request(method,
                                       url,
                                       headers=headers,
                                       params=params,
                                       data=data,
                                       ssl_context=self._SSL_CONTEXT_) as response:
                if response.status == 401:
                    raise WrongToken("Wrong token!")
                elif response.status == 403:
                    raise PermError("Not enough permissions to access this method")
                else:
                    return await response.json()
