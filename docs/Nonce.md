# Nonce
* Class containing nonce generation methods.
---
## Usage example
```python
from pyfreekassa import Configuration, Nonce

Configuration.configure(
    nonce_generation_method = Nonce.Methods.TXT,
    nonce_path = 'nonce.txt'
)
```
---
* Supported nonce generation methods:
1. TXT
2. PICKLE
* Supported nonce path types:
1. `nonce.txt` | With provided file extension, depending on nonce generation method
2. `nonce` | Without provided file extension, extension will be added automatically, depending on nonce generation method