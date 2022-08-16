from app import ws_client, db, pump
from models.clock import Clock
from models.slot import Slot

from services.web_socket import WebSocketRequest, WebSocketResponse


@ws_client.on('GET#SLOTS')
def slots_get(req: WebSocketRequest, res: WebSocketResponse):
    slot_repo = db.get_repository(Slot)
    slots = slot_repo.find_all()
    print(slots, [slot.format() for slot in slots])
    res.send({
        'slots': [slot.format() for slot in slots]
    })


@ws_client.on('POST#SLOT')
def slot_post(req: WebSocketRequest, res: WebSocketResponse):
    slot_repo = db.get_repository(Slot)
    slot = Slot()
    slot.temperature = req.data['temperature']
    slot_repo.insert(slot)
    pump.refresh_slot()
    res.send({
        'slot': slot.format()
    })


@ws_client.on('PUT#SLOT')
def slot_put(req: WebSocketRequest, res: WebSocketResponse):
    slot_repo = db.get_repository(Slot)
    slot: Slot = slot_repo.find('id', req.data['slotId'])
    if slot:
        slot.temperature = req.data['temperature']
        slot_repo.update(slot)
        pump.refresh_slot()
        res.send({
            'slot': slot.format()
        })
    else:
        res.send({
            'error': 'SLOT_NOT_FOUND'
        }, 'ERROR')


@ws_client.on('DELETE#SLOT')
def slot_delete(req: WebSocketRequest, res: WebSocketResponse):
    slot_repo = db.get_repository(Slot)
    slot = slot_repo.find('id', req.data['slotId'])
    if slot:
        clock_repo = db.get_repository(Clock)
        clocks = clock_repo.find_all(lambda clock: clock.slotId == slot.id)
        for clok in clocks:
            clock_repo.delete(clok)
        slot_repo.delete(slot)
        pump.refresh_slot()
        res.send()
    else:
        res.send({
            'error': 'SLOT_NOT_FOUND'
        }, 'ERROR')


@ws_client.on('GET#CLOCKS')
def clock_post(req: WebSocketRequest, res: WebSocketResponse):
    slot_repo = db.get_repository(Slot)
    slot: Slot = slot_repo.find('id', req.data['slotId'])
    if slot:
        clock_repo = db.get_repository(Clock)
        clocks = clock_repo.find_all(lambda clock: clock.slotId == slot.id)
        res.send({
            'clocks': [clock.format() for clock in clocks]
        })
    else:
        res.send({
            'error': 'SLOT_NOT_FOUND'
        }, 'ERROR')


@ws_client.on('POST#CLOCK')
def clock_post(req: WebSocketRequest, res: WebSocketResponse):
    slot_repo = db.get_repository(Slot)
    slot: Slot = slot_repo.find('id', req.data['slotId'])
    if slot:
        clock = Clock()
        data = req.data
        clock.slotId = slot.id
        clock.start = data['start']
        clock.end = data['end']
        clock.enable = data['enable']
        db.get_repository(Clock).insert(clock)
        pump.refresh_slot()
        res.send({
            'clock': clock.format()
        })
    else:
        res.send({
            'error': 'SLOT_NOT_FOUND'
        }, 'ERROR')


@ws_client.on('PUT#CLOCK')
def clock_put(req: WebSocketRequest, res: WebSocketResponse):
    clock_repo = db.get_repository(Clock)
    clock: Clock = clock_repo.find('id', req.data['clockId'])
    if clock:
        data = req.data
        clock.start = data['start']
        clock.end = data['end']
        clock.enable = data['enable']
        clock_repo.update(clock)
        pump.refresh_slot()
        res.send({
            'clock': clock.format()
        })
    else:
        res.send({
            'error': 'CLOCK_NOT_FOUND'
        }, 'ERROR')


@ws_client.on('DELETE#CLOCK')
def clock_put(req: WebSocketRequest, res: WebSocketResponse):
    clock_repo = db.get_repository(Clock)
    clock: Slot = clock_repo.find('id', req.data['clockId'])
    if clock:
        clock_repo.delete(clock)
        pump.refresh_slot()
        res.send()
    else:
        res.send({
            'error': 'CLOCK_NOT_FOUND'
        }, 'ERROR')
