import binascii
import random
import socket
import json
import re

import time
import ustruct
from machine import Timer
from tools.config import Config

OP_CONT = 0x0
OP_TEXT = 0x1
OP_BYTES = 0x2
OP_CLOSE = 0x8
OP_PING = 0x9
OP_PONG = 0xa

CLOSE_OK = 1000
CLOSE_GOING_AWAY = 1001
CLOSE_PROTOCOL_ERROR = 1002
CLOSE_DATA_NOT_SUPPORTED = 1003
CLOSE_BAD_DATA = 1007
CLOSE_POLICY_VIOLATION = 1008
CLOSE_TOO_BIG = 1009
CLOSE_MISSING_EXTN = 1010
CLOSE_BAD_CONDITION = 1011

IDLE = 0
READY = 1
CONNECTING = 2
CLOSED = 3


class WebSocket(Config):
    client: socket.Socket
    timer: Timer
    config: object or None
    lastPing: int
    status: int

    def __init__(self):
        super().__init__('web-socket')
        self.client = socket.socket()
        self.timer = Timer(-1)
        self.listener = {}
        self.lastPingTime = 0
        self.status = IDLE
        self.config = None
        self.load_config()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def loop(self):
        if self.status != READY:
            return
        try:
            now = time.time()
            if now - self.lastPingTime > 5:
                self.close()
                return
            data = self.client.readline()
            if not data:
                return
            json_str = re.search('{.*}', data)
            if not json_str:
                return
            data_json = json.loads(json_str.group(0))
            id = data_json.get('id')
            event = data_json.get('event')
            if event == 'PING':
                self.lastPingTime = now
                self.send(id, 'PONG')
            callback = self.listener.get(event)
            if callback:
                callback(data_json.get('data'), id)
        except Exception as e:
            print('socket loop error', e)

    def write_frame(self, opcode, data: bytes):
        length = len(data)

        byte1 = 0x80
        byte1 |= opcode

        byte2 = 0x80

        if length < 126:
            byte2 |= length
            self.client.write(ustruct.pack('!BB', byte1, byte2))
        elif length < (1 << 16):
            byte2 |= 126
            self.client.write(ustruct.pack('!BBH', byte1, byte2, length))
        elif length < (1 << 64):
            byte2 |= 127
            self.client.write(ustruct.pack('!BBQ', byte1, byte2, length))
        else:
            raise Exception('Value error')

        mask_bits = ustruct.pack('!I', random.getrandbits(32))
        self.client.write(mask_bits)

        data = bytes(b ^ mask_bits[i % 4] for i, b in enumerate(data))
        self.client.write(data)

    def send(self, id: str, event: str, data: object or str = ''):
        json_data = json.dumps({
            'id': id,
            'event': event,
            'data': data
        })
        json_data_encoded = json_data.encode('utf-8')
        self.write_frame(OP_TEXT, json_data_encoded)

    def on(self, event: str):
        def wrapper(callback):
            def inner(req_data, id):
                callback(req_data, lambda data: self.send(id, 'CALLBACK', data))

            self.listener[event] = inner

        return wrapper

    def close(self, code=CLOSE_OK, reason=''):
        self.status = CLOSED
        buf = ustruct.pack('!H', code) + reason.encode('utf-8')
        self.write_frame(OP_CLOSE, buf)
        self.client.close()

    def connect(self):
        try:
            self.status = CONNECTING
            self.client = socket.socket()

            host = self.config.get('host')
            port = self.config.get('port')
            path = self.config.get('path')
            config_authorization = self.config.get('authorization')

            def set_header(name: str, value: str or bytes = None):
                data: str = name
                if value:
                    data += ':'
                    data += value
                data += '\r\n'
                self.client.write(data.encode())

            self.client.connect((host, port))

            ws_key = binascii.b2a_base64(bytes(random.getrandbits(8) for _ in range(16)))[:-1]
            authorization = f"{config_authorization.get('device_id')}:{config_authorization.get('device_key')}"

            set_header(f"GET {path} HTTP/1.1")
            set_header('Host', f'{host}:{port}')
            set_header('Connection', 'Upgrade')
            set_header('Upgrade', 'websocket')
            set_header('Sec-WebSocket-Key', ws_key.decode())
            set_header('Sec-WebSocket-Version', '13')
            set_header('auth', authorization)
            set_header('')

            res = self.client.readline()[:-2]
            assert res.startswith(b'HTTP/1.1 101 '), res

            self.client.setblocking(False)
            self.lastPingTime = time.time()
            self.status = READY
        except Exception as e:
            self.status = CLOSED
