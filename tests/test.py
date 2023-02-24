import asyncio
from asyncqiwi import AsyncQiwi

qiwi = AsyncQiwi(
	phone="79000000000",
	token="XXXXXXXXXXXX",
	secret_key="XXXXXXXXXXXX"
)


async def start():
	# получаем актуальный баланс Qiwi (дефолт рубли)
	balance = await qiwi.getBalance()
	print(balance)

	# создаем счет для оплаты на Ваш QIwi
	bill = await qiwi.create(
		amount=400,
		comment="Мой первый счет"
	)
	print(bill.bill_id)  # это выведет индентификатор счета
	print(bill.pay_url)  # выведет ссылку для оплаты счета

	# получаем статус счета, оплачен он иль нет
	check_bill = await qiwi.status(
		bill_id=332243
	)
	print(check_bill.status)  # выведет статус счета

	# закрываем неоплаченный счет
	reject = await qiwi.reject(
		bill_id=4404403
	)
	print(reject.status)  # статус счета при попытке закрыть его преждевременно


if __name__ == "__main__":
	asyncio.run(start())

