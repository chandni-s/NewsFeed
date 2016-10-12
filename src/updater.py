from threading import Thread
import time


class Updater(Thread):
    """Calls a function at a set frequency on its own thread.
    """

    def __init__(self, frequency, function):
        """(Updater, int, function) -> None
        Creates a thread that runs the given function at the given frequency,
        in seconds.
        """
        # Set the thread to running, and call the thread constructor
        # to create the thread.
        self.running = True
        self.frequency = frequency
        self.function = function
        Thread.__init__(self)

    def run(self):
        """(Updater) -> None
        The update thread. Calls the function at the frequency repeatedly
        until the thread needs to stop.
        """
        while self.running:
            self.function()
            time.sleep(self.frequency)