# Pyfreekassa

> Supports all freekassa API methods (Need testing)

> Asynchronous

> Has built-in tools like OrderID and Nonce generators
 
## Usage example:
```python
from pyfreekassa import Configuration, FrekassaApi, Nonce
import asyncio

Configuration.configure(
    merchant_id = 123,
    first_secret = "abc",
    second_secret = "def", 
    wallet_api_key = "qwerty123",
    nonce_generation_method = Nonce.Methods.TXT,
    nonce_path = "nonce.txt"
)
fk = FrekassaApi(config=Configuration(), payment_order_id="12345", wallet_id=1)

async def main():
    print(await fk.get_payment_systems())

if __name__ == "__main__":
    asyncio.run(main())
```

## Feel free to contribute.