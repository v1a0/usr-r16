# USR-R16 / USR-R16-T

Simpe USR-R16 / USR-R16-T boards controller class

```python
from usrr16 import UsrR16

r16 = UsrR16(host='192.168.0.99', port=8899, password='admin')
r16.turn_off_all()

r16.invert(relay=1)
r16.turn_on(relay=2)
r16.turn_off(relay=2)
```


```
pip install usrr16
```

> Based on [@wowks/USR-R16](https://github.com/wowks/USR-R16) and [xtodx/php-USR-R16](https://github.com/xtodx/php-USR-R16)
> 
> thank you
