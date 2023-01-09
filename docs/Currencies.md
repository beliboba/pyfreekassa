# Currencies
* Class containing all the currencies supported by FreeKassa.
---
## Usage example
```python
from pyfreekassa import Currencies, FreekassaApi
import asyncio

fk = FreekassaApi(...)

async def main():
    url = await fk.get_form_url(payment_currency=Currencies.Visa.RUB)
    print(url)

if __name__ == '__main__':
    asyncio.run(main())
```
* As seen here, you need to pass currency to some methods. `Currencies` class is used to get the currency code. However, you can pass currency code yourself if you know it.
