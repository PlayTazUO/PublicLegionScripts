# See the example at the bottom for how to use this in your script
# Copy this file into your LegionScripts folder, then use the example at the bottom in your scripts
# from _timers import TimerManager
# mgr = TimerManager()
# mgr.add_timer("greet_once", 3.0, hello, repeat=False, args=("Alice",))
# mgr.add_timer("greet_repeat", 2.0, hello, repeat=True, args=("Bob",))
# while not API.StopRequested:
#   mgr.update()
#   API.Pause(0.1)


import time

class Timer:
    def __init__(self, name, duration, callback, repeat=False, args=(), kwargs=None):
        self.name = name
        self.duration = float(duration)  # duration in seconds
        self.end_time = time.time() + self.duration
        self.callback = callback
        self.repeat = bool(repeat)
        self.args = args
        self.kwargs = {} if kwargs is None else dict(kwargs)

    def check(self):
        current_time = time.time()
        if current_time >= self.end_time:
            try:
                self.callback(*self.args, **self.kwargs)
            except Exception:
                # swallow callback exceptions to keep manager running
                pass
            if self.repeat:
                # reset for the next round
                self.end_time = current_time + self.duration
                return False  # keep timer
            return True  # signal removal
        return False  # not finished

    def reset(self):
        self.remaining = self.duration

class TimerManager:
    def __init__(self):
        self._timers = {}  # name -> Timer

    def add_timer(self, name, duration, callback, repeat=False, args=(), kwargs=None):
        """
        Add a named timer.
        duration: integer number of ticks until callback runs.
        callback: callable invoked when timer elapses.
        repeat: if True, timer restarts automatically.
        """
        if name in self._timers:
            raise KeyError(f"Timer '{name}' already exists")
        self._timers[name] = Timer(name, duration, callback, repeat, args, kwargs)

    def remove_timer(self, name):
        self._timers.pop(name, None)

    def has_timer(self, name):
        return name in self._timers

    def get_remaining(self, name):
        t = self._timers.get(name)
        if t is None:
            return None
        return max(0, t.end_time - time.time())

    def reset_timer(self, name):
        t = self._timers.get(name)
        if t:
            t.end_time = time.time() + t.duration

    def update(self):
        """
        Check all timers against the current time.
        Timers that have elapsed will trigger their callbacks.
        Non-repeating timers are removed automatically after triggering.
        """
        # collect names to remove after checking
        to_remove = []
        # iterate over a list copy to allow modification
        for name, timer in list(self._timers.items()):
            finished = timer.check()
            if finished:
                to_remove.append(name)
        for name in to_remove:
            self.remove_timer(name)

# Example usage in a script
def example():
    #from _timers import TimerManager #<--- Add this line to your script
    def hello(name):
        print(f"Hello, {name}! Time: {time.time():.2f}")

    mgr = TimerManager()
    mgr.add_timer("greet_once", 3.0, hello, repeat=False, args=("Alice",))
    mgr.add_timer("greet_repeat", 2.0, hello, repeat=True, args=("Bob",))

    while not API.StopRequested:
        mgr.update()
        API.Pause(0.1)
