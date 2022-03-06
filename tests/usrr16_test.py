import unittest
import time
from usrr16 import UsrR16

delay = 0.1     # if tests stacked, set it a little bit bigger


class TestUsrR16(unittest.TestCase):
    """
    Set right data in setUpClass method to connect to your device !!!

    P.S. currently UsrR16.state() is trustable function
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.relay_r16 = UsrR16(host='192.168.0.27')

    def tearDown(self) -> None:
        # turn of all
        self.relay_r16.sock.send(bytearray(b'U\xaa\x00\x03\x00\x05\x00\x03'))
        self.relay_r16.sock.recv(512)

    def test_turn_on_off(self):
        for rel in range(1, 17):
            # on test
            time.sleep(delay)
            self.relay_r16.turn_on(rel)
            time.sleep(delay)
            self.assertTrue(self.relay_r16.state(rel))

            # off test
            time.sleep(delay)
            self.relay_r16.turn_off(rel)
            time.sleep(delay)
            self.assertFalse(self.relay_r16.state(rel))

    def test_invert(self):
        # for turned on relay
        for rel in range(1, 17):
            time.sleep(delay)
            self.relay_r16.turn_on(rel)
            time.sleep(delay)
            self.assertTrue(self.relay_r16.state(rel))

            time.sleep(delay)
            self.relay_r16.invert(rel)
            time.sleep(delay)
            self.assertFalse(self.relay_r16.state(rel))

        # for turned off relay
        for rel in range(1, 17):
            time.sleep(delay)
            self.relay_r16.turn_off(rel)
            time.sleep(delay)
            self.assertFalse(self.relay_r16.state(rel))

            time.sleep(delay)
            self.relay_r16.invert(rel)
            time.sleep(delay)
            self.assertTrue(self.relay_r16.state(rel))

    def test_turn_off_all(self):
        # turning of all relays
        for rel in range(1, 17):
            time.sleep(delay)
            self.relay_r16.turn_on(rel)
            time.sleep(delay)
            self.assertTrue(self.relay_r16.state(rel))

        time.sleep(delay)
        self.relay_r16.turn_off_all()

        # checking is all off
        for rel in range(1, 17):
            time.sleep(delay)
            print('.', end='')
            self.assertFalse(self.relay_r16.state(rel))

