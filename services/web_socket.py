import binascii
import random
import json
import time
import ustruct
import socket

from tools.config import Config
from tools.id import id_generator

OP_TEXT_REQ = 0x81
OP_TEXT_RES = 0x51
OP_CLOSE = 0x58
OP_PING = 0x59
OP_PONG = 0x0a

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


def read_frame(soc: socket.Socket):
    byte1 = soc.recv(1)
    if byte1:
        byte2 = soc.recv(1)
        if byte2.decode() == '~':
            soc.recv(2)
        data = soc.recv(1000)

        return int(binascii.hexlify(byte1).decode()), data
    return None


def write_frame(soc: socket.Socket, opcode, data: bytes):
    length = len(data)
    byte1 = 0x80
    byte1 |= opcode
    byte2 = 0x80

    if length < 126:
        byte2 |= length
        soc.write(ustruct.pack('!BB', byte1, byte2))
    elif length < (1 << 16):
        byte2 |= 126
        soc.write(ustruct.pack('!BBH', byte1, byte2, length))
    elif length < (1 << 64):
        byte2 |= 127
        soc.write(ustruct.pack('!BBQ', byte1, byte2, length))
    else:
        raise Exception('Value error')

    mask_bits = ustruct.pack('!I', random.getrandbits(32))
    soc.write(mask_bits)

    data = bytes(b ^ mask_bits[i % 4] for i, b in enumerate(data))
    soc.write(data)


class WebSocketRequest:
    id: str
    event: str
    data: dict or None

    def __init__(self, id: str, event: str, data: dict or None):
        self.id = id
        self.event = event
        self.data = data


class WebSocketResponse:
    soc: socket.Socket
    id: str

    def __init__(self, soc: socket.Socket, id: str):
        self.soc = soc
        self.id = id

    def send(self, data=None, status: str = 'OK'):
        frame_data = {
            'id': self.id,
            'event': 'CALLBACK',
            'status': status
        }
        if data:
            frame_data['data'] = data
        frame_data_encoded = json.dumps(frame_data).encode('utf-8')
        write_frame(self.soc, OP_TEXT_REQ, frame_data_encoded)


class WebSocketClient:
    soc: socket.Socket
    last_ping: int
    status: int
    config: Config

    def __init__(self):
        self.listener = {}
        self.last_ping_time = 0
        self.status = IDLE
        self.config = Config('web-socket')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def loop(self):
        if self.status != READY:
            return
        now_time = time.time()
        try:
            if now_time - self.last_ping_time > 10:
                self.close()
                return
            frame = read_frame(self.soc)
            if frame is None:
                return
            opcode, raw_data = frame
            if opcode == OP_TEXT_RES:
                json_frame = json.loads(raw_data.decode('utf-8'))
                print('json_frame', json_frame)
                event = json_frame['event']
                callback = self.listener.get(event)
                if callback:
                    id = json_frame['id']
                    data = json_frame.get('data')
                    req = WebSocketRequest(id, event, data)
                    res = WebSocketResponse(self.soc, id)
                    callback(req, res)
            elif opcode == OP_PING:
                write_frame(self.soc, OP_PONG, raw_data)
                self.last_ping_time = now_time
            elif opcode == OP_CLOSE:
                self.status = CLOSED
        except Exception as e:
            return e

    def send(self, event: str, data: dict):
        if self.status != READY:
            return
        frame_data = {
            'id': id_generator(10),
            'event': event,
            'data': data
        }
        json_data_encoded = json.dumps(frame_data).encode('utf-8')
        write_frame(self.soc, OP_TEXT_REQ, json_data_encoded)

    def on(self, event: str):
        def wrapper(callback):
            self.listener[event] = callback

        return wrapper

    def write_header(self, name: str, value: str or bytes = None):
        data: str = name
        if value:
            data += ':'
            data += value
        data += '\r\n'
        self.soc.write(data.encode())

    def connect(self):
        host = self.config.get('host')
        port = self.config.get('port')
        path = self.config.get('path')
        config_authorization = self.config.get('authorization')
        authorization = f"{config_authorization.get('device_id')}:{config_authorization.get('device_key')}"

        try:
            self.status = CONNECTING
            soc = socket.socket()
            soc.connect((host, port))
            ws_key = binascii.b2a_base64(bytes(random.getrandbits(8) for _ in range(16)))[:-1]

            def set_header(name: str, value: str or bytes = None):
                data: str = name
                if value:
                    data += ':'
                    data += value
                data += '\r\n'
                soc.write(data.encode())

            set_header(f"GET {path} HTTP/1.1")
            set_header('Host', f'{host}:{port}')
            set_header('Connection', 'Upgrade')
            set_header('Upgrade', 'websocket')
            set_header('Sec-Websocket-Key', ws_key.decode())
            set_header('Sec-Websocket-Version', '13')
            set_header('auth', authorization)
            set_header('')

            res = soc.readline()[:-2]
            assert res.startswith(b'HTTP/1.1 101 '), res

            soc.setblocking(False)
            self.status = READY
            self.last_ping_time = time.time()
            self.soc = soc
        except Exception as e:
            self.status = CLOSED
            print(e)

    def close(self, code=CLOSE_OK, reason=''):
        self.status = CLOSED
        buf = ustruct.pack('!H', code) + reason.encode('utf-8')
        write_frame(self.soc, OP_CLOSE, buf)
        self.soc.close()
