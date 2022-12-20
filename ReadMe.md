# OpenVk-API

Raw API for [OpenVK](https://github.com/openvk/openvk)

```
pip install openvk-api
```

Use [OpenVk Docs](https://docs.openvk.su/openvk_engine/api/description/) to use `OpenVkApiMethod`

## Quick example

```python
from openvk_api import OpenVkClient
# Use token
client = OpenVkClient(token="sdflksdfkljssldkjgsdg-jill")
# Use login and password
client = OpenVkClient()
client = client.auth_with_password(login="fckptn@gg.su", password="Hydra")

api = client.get_api()
print(api.messages.send(user_id=10484, message="Hello, developer"))
```

## Links
[Dev's OpenVk.uk profile](https://openvk.su/id10484)
[Gitter.im chat](https://gitter.im/openvk-py/openvk-api-py) - [Matrix](https://matrix.to/#/#openvk-py_openvk-api-py:gitter.im)
