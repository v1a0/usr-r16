from time import sleep
from usrr16 import UsrR16


def street():
    for i in range(1, 8):
        r16.invert(i)
        sleep(0.1)
        r16.invert(i+8)
        sleep(0.1)


def snake():
    for i in range(1, 16+1):
        r16.invert(i)
        sleep(0.1)


def double():
    for i in range(1, 16+1):
        r16.invert(i)
        sleep(0.1)
        r16.invert(16-i)
        sleep(0.1)


def zigzag():
    sleep(0.2)
    for i in range(1, 16+1):
        if i > 1:
            r16.invert(i-1)
            sleep(0.2)
            r16.invert(17 - i)
            sleep(0.2)

        r16.invert(i)
        sleep(0.2)
        r16.invert(16-i)
        sleep(0.2)


r16 = UsrR16(host='192.168.0.23', port=8899, password='admin')
# r16 = UsrR16(host='192.168.0.27')

street()
print(r16.state(1))

r16.turn_off(1)
print(r16.state(1))
print(r16.state(2))

r16.turn_off_all()

