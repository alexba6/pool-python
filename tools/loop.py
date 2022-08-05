import time


class LoopCallback:
    callback: any
    period: int
    name: str
    last_call_time_ms: int

    def __init__(self, callback, period: int, name: str):
        self.callback = callback
        self.period = period
        self.name = name
        self.last_call_time_ms = 0

    def loop(self, now_time_ms: int):
        if now_time_ms - self.last_call_time_ms >= self.period:
            self.last_call_time_ms = now_time_ms
            try:
                self.callback()
            except Exception as e:
                print(f'Error loop - {self.name}', e)


class Loop:
    callbacks: list

    def __init__(self):
        self.callbacks = []

    def add_callback(self, **kwargs):
        period = kwargs.get('period')
        func = kwargs.get('callback')
        assert func, Exception('Callback not found')
        if not period:
            period = -1
        self.callbacks.append(LoopCallback(func, period, kwargs.get('name')))

    def add(self, **kwargs):
        def wrapper(func):
            kwargs['callback'] = func
            self.add_callback(**kwargs)
        return wrapper

    def loop(self):
        now_time_ms = time.time_ns() / 10**6
        for callback in self.callbacks:
            callback.loop(now_time_ms)


