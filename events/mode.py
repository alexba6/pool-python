from services.web_socket import WebSocketRequest, WebSocketResponse

from services.pump import AUTO, ON, OFF
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


@ws_client.on('ACTION#GET#PUMP')
def pump_action_get(req: WebSocketRequest, res: WebSocketResponse):
    res.send({
        'state': pump.state,
        'freeze': pump.mode not in [AUTO, ON, OFF],
        'enableGroup': pump.mode
    })


@ws_client.on('ACTION#SET#PUMP')
def pump_action_set(req: WebSocketRequest, res: WebSocketResponse):
    mode = req.data['group']['name']
    pump.change_mode(mode)
    res.send({
        'state': pump.state,
        'freeze': pump.mode not in [AUTO, ON, OFF],
        'enableGroup': pump.mode
    })

