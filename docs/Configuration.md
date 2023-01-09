# Configuration
* Configuration class. Should be passed to [FreekassaApi](FreekassaApi.md) class.
---
## Usage example
```python
from pyfreekassa import Configuration, Nonce

Configuration.configure(
    merchant_id = 123,
    first_secret = "abc",
    second_secret = "def", 
    wallet_api_key = "qwerty123",
    nonce_generation_method = Nonce.Methods.TXT,
    nonce_path = "nonce.txt"
)
```
* As seen here you need to pass your merchant ID, first and second secrets, wallet API key, [nonce generation method and nonce path](Nonce.md).