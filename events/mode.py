from services.web_socket import WebSocketRequest, WebSocketResponse

from app import socket, pump


@socket.on('POST#MODE')
def pump_post_mode(req: WebSocketRequest, res: WebSocketResponse):
    mode = req.data['mode']
    pump.change_mode(mode)
    res.send({
        'mode': pump.mode,
        'state': pump.state
    })


@socket.on('GET#MODE')
def pump_post_mode(req: WebSocketRequest, res: WebSocketResponse):
    res.send({
        'mode': pump.mode,
        'state': pump.state
    })

