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
	bill = await qiwi.createBill(
		amount=400,
		comment="Мой первый счет"
	)
	print(bill["payUrl"])  # это выведет ссылку на счет

	# получаем статус счета, оплачен он иль нет
	check_bill = await qiwi.checkingBill(
		bill_id=332243
	)
	print(check_bill)


if __name__ == "__main__":
	asyncio.run(start())
