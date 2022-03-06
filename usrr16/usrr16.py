import socket


class UsrR16:
    def __init__(self, host: str, port: int = 8899, password: str = "admin"):
        """
        Main class to interact with USR-R16 Relay

        :param host: str
            IP address of host as string, example: "192.168.0.42"
        :param port: int
            Port for connection if custom, default value 8899
        :param password: str
            Password to login on device, default "admin"
        """

        self.host = host
        self.port = port
        self.sock = socket.socket()

        self.sock.connect((host, port))
        self.auth(password=password)

    def send_recv(self, data: bytes, bufsize: int = 256) -> bytes:
        """
        Send data and return the receive as bytes

        :param data: bytes
            Data to send sock.send
        :param bufsize: int
            Buffer size for sock.recv
        :return:
        """

        self.sock.send(data)
        return self.sock.recv(bufsize)

    def auth(self, password: str):
        """
        Authorisation on device by password

        :param password: str
            Password to login on device
        """

        answer = self.send_recv(
            data=password.encode() + b'\x0d' + b'\x0a',
            bufsize=1024
        )

        if answer != b'OK':
            raise ConnectionError("Authorisation failed | Password incorrect")

    @staticmethod
    def req_gen(relay: int, command: int) -> bytearray:
        """
        Generate byte-command
        0x55 0xaa 0x00 %s 0x00 %s %s %s

        :param relay: Relay number 0-16 (0 - all)
        :param command: 1 - off, 2 - on, 3 - invert
        :return: bytearray
        """

        if relay < 0 or relay > 16:
            raise ValueError(f"Relay value out of range, expected 1-16, got {relay}")

        return bytearray([0x55, 0xAA, 0x00, 3, 0x00, command, relay, 3])

    def state(self, relay: int) -> bool:
        """
        Get relay status as boolean

        > by @horga83

        :param relay: int
            Relay's id
        :return: bool
            Is this relay turned on
        """

        # mask for each I/O point, to find state and returned state with mask[n]
        mask = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]

        resp = self.send_recv(self.req_gen(relay=relay, command=0x0a))

        # About resp
        # Get the 6th byte of the message if relay < 9 else 7th byte
        # b'\xaa\x55\x00\x04\x00\x81\x08\x00\x8d'
        #                            ^ or ^

        if relay < 9:
            mask_byte = resp[6]
        else:
            mask_byte = resp[7]

        return mask_byte & mask[relay] == mask[relay]

    def turn_off(self, relay: int):
        """
        Turn off relay

        :param relay: int
            Relay's id
        """

        self.send_recv(self.req_gen(relay=relay, command=1))

    def turn_on(self, relay: int):
        """
        Turn on relay

        :param relay: int
            Relay's id
        """

        self.send_recv(self.req_gen(relay=relay, command=2))

    def invert(self, relay: int):
        """
        Invert relay's state

        :param relay: int
            Relay's id
        """

        self.send_recv(self.req_gen(relay=relay, command=3))

    def turn_off_all(self):
        """
        Turn off all relays

        """

        self.send_recv(self.req_gen(relay=0, command=5))
