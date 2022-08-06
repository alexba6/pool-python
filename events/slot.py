from app import socket, pump
from models.slots import TempSlot


def get_temp_slot_index(id: str):
    for i in range(len(pump.config['temp_slots'])):
        temp_slot = pump.config['temp_slots'][i]
        if id == temp_slot['id']:
            return i
    return None


@socket.on('GET#SLOTS')
def get_slots(req, res):
    res('OK', {
        'temp_slots': pump.config['temp_slots']
    })


@socket.on('POST#TEMP_SLOT')
def post_temp_slot(req, res):
    temp_slot = TempSlot()
    temp_slot.temperature = req['temperature']
    pump.config['temp_slots'].append(temp_slot.object())
    pump.save_config()
    pump.refresh_temp_slot()
    res('OK', {
        'temp_slot': temp_slot.object()
    })


@socket.on('DELETE#TEMP_SLOT')
def post_temp_slot(req, res):
    id = req['id']
    temp_slot_index = get_temp_slot_index(id)
    if temp_slot_index is None:
        res('ERROR', {
            'error': 'Id not found'
        })
        return
    pump.config['temp_slots'].pop(temp_slot_index)
    pump.save_config()
    pump.refresh_temp_slot()
    res('OK')


@socket.on('UPDATE#TEMP_SLOT')
def post_temp_slot(req, res):
    id = req['id']
    temp_slot_index = get_temp_slot_index(id)
    if temp_slot_index is None:
        res('ERROR', {
            'error': 'Id not found'
        })
        return
    temperature = req['temperature']
    pump.config['temp_slots'][temp_slot_index]['temp'] = temperature
    pump.save_config()
    pump.refresh_temp_slot()
    res('OK', {
        'temp_slots': pump.config['temp_slots'][temp_slot_index]
    })
