from app import socket, pump


@socket.on('POST#MODE')
def pump_post_mode(req, res):
    mode = req['mode']
    pump.change_mode(mode)
    res('OK', {
        'mode': pump.mode,
        'state': pump.state
    })


@socket.on('GET#MODE')
def pump_get_mode(req, res):
    res('OK', {
        'mode': pump.mode,
        'state': pump.state
    })


