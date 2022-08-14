from services.web_socket import WebSocketRequest, WebSocketResponse

from app import ws_client, pump


@ws_client.on('POST#MODE')
def pump_post_mode(req: WebSocketRequest, res: WebSocketResponse):
    mode = req.data['mode']
    pump.change_mode(mode)
    res.send({
        'mode': pump.mode,
        'state': pump.state
    })


@ws_client.on('GET#MODE')
def pump_post_mode(req: WebSocketRequest, res: WebSocketResponse):
    print('Getting mode')
    res.send({
        'mode': pump.mode,
        'state': pump.state
    })

