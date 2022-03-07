# USR-R16 / USR-R16-T

Simpe USR-R16 / USR-R16-T boards controller class

# Example

```python
from usrr16 import UsrR16

r16 = UsrR16(host='192.168.0.99', port=8899, password='admin')
r16.turn_off_all()

r16.invert(relay=1)
r16.turn_on(relay=2)
r16.turn_off(relay=2)

r16.turn_on(3)
print(r16.state(3)) # True

r16.turn_off(3)
print(r16.state(3)) # False
```

# Installation

```
pip install usrr16
```


# Addons

Check out example of control application. In examples/usrr16-app.py

```shell
┌──────────────────────────────────────────────────────────────────────────────┐
│                              USR-R16 Relay Board                             │
│                           Control and Status Window                          │
│                                                                              │
│ ┌─────────┐┌───┐   ┌─────────┐┌───┐    ┌─────────┐┌───┐    ┌─────────┐┌───┐  │
│1│ Relay 1 ├┤OFF│  5│ Relay 5 ├┤OFF│   9│ Relay 9 ├┤OFF│  13│ Relay 13├┤ON │  │
│ └─────────┘└───┘   └─────────┘└───┘    └─────────┘└───┘    └─────────┘└───┘  │
│                   +--[Control Selection]---+                                 │
│ ┌─────────┐┌───┐  |                        |─────┐┌───┐    ┌─────────┐┌───┐  │
│2│ Relay 2 ├┤OFF│  |          On            |ay 10├┤OFF│  14│ Relay 14├┤ON │  │
│ └─────────┘└───┘  |         █Off█          |─────┘└───┘    └─────────┘└───┘  │
│                   |         Cycle          |                                 │
│ ┌─────────┐┌───┐  |                        |─────┐┌───┐    ┌─────────┐┌───┐  │
│3│ Relay 3 ├┤OFF│  |                        |ay 11├┤OFF│  15│ Relay 15├┤ON │  │
│ └─────────┘└───┘  | <Enter> <UP> <DN> 'q'  |─────┘└───┘    └─────────┘└───┘  │
│                   +------------------------+                                 │
│ ┌─────────┐┌───┐   ┌─────────┐┌───┐    ┌─────────┐┌───┐    ┌─────────┐┌───┐  │
│4│ Relay 4 ├┤OFF│  8│ Relay 8 ├┤OFF│  12│ Relay 12├┤OFF│  16│ Relay 16├┤ON │  │
│ └─────────┘└───┘   └─────────┘└───┘    └─────────┘└───┘    └─────────┘└───┘  │
│                                                                              │
│──────────────────────────────────────────────────────────────────────────────│
│ EXIT: Q  | Use Arrow keys, then press <ENTER> to control relay  | All Off: X │
│──────────────────────────────────────────────────────────────────────────────│
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

> Contributors: @v1a0, @horga83
>
> Based on [@wowks/USR-R16](https://github.com/wowks/USR-R16) and [xtodx/php-USR-R16](https://github.com/xtodx/php-USR-R16)
> 
> Thank you!
