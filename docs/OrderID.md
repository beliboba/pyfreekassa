# OrderID
* Class used to generate OrderID.
---
## Usage example
```python
from pyfreekassa import OrderId, FreekassaApi

fk = FreekassaApi(
    method=OrderId.Methods.random_int
)
```
* Method determines how `order_id` will be generated. 
* While methods present in `OrderId.Methods` generate random `order_id`, you can use pass your own `order_id` argument in some functions.