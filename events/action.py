from services.web_socket import WebSocketRequest, WebSocketResponse

from services.pump import AUTO, ON, OFF
from app import ws_client, pump


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

