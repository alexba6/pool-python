from tools.ds1307 import DS1307
from tools.time_convert import get_sec

ALLOW_OFFSET = 10


class ScheduleCallback:
    active_time: tuple
    active_time_sec: int
    name: str
    callback: any
    called: bool

    def __init__(self, active_time: tuple, callback, name: str):
        self.active_time = active_time
        self.callback = callback
        self.name = name
        self.called = False
        self.active_time_sec = get_sec(active_time)

    def loop(self, now_dt: tuple):
        delta = get_sec(now_dt) - self.active_time_sec
        if 0 <= delta <= ALLOW_OFFSET and not self.called:
            self.called = True
            try:
                self.callback()
            except Exception as e:
                print(f'Error schedule - {self.name}', e)
        if delta > ALLOW_OFFSET and self.called:
            self.called = False


class Schedule:
    ds: DS1307
    callbacks: list

    def __init__(self, ds: DS1307):
        self.ds = ds
        self.callbacks = []

    def add_callback(self, **kwargs):
        callback = kwargs.get('callback')
        active_time = kwargs.get('active_time')
        assert callback, Exception('Callback not found')
        assert active_time, Exception('Time not found')
        self.callbacks.append(ScheduleCallback(active_time, callback, kwargs.get('name')))

    def add(self, active_time: tuple, **kwargs):
        def wrapper(func):
            kwargs['callback'] = func
            kwargs['active_time'] = active_time
            self.add_callback(**kwargs)
        return wrapper

    def loop(self):
        now_dt = self.ds.datetime()[4:7]
        for callback in self.callbacks:
            callback.loop(now_dt)

