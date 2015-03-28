from threading import Timer


class WatchDog(object):
    """
        This WatchDog class is used for keeping track of heart beat message.
        It calls timer every X seconds.
    """
    def __init__(self, timeout, user_name, user_handler):
        self.timeout = timeout
        self.handler = user_handler
        self.user_name = user_name
        self.timer = Timer(self.timeout, self.handler, self.user_name)

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.cancel()

    def reset(self):
        self.timer.cancel()
        self.timer = Timer(self.timeout, self.handler, self.user_name)

    def default_handler(self):
        raise self
