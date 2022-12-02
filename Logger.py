import itertools
import threading
from time import sleep

class Logger():
    def __init__(self) -> None:
        self._file : str = ".\\"
        self._oper : str = "Initializing"
        self.done : bool = False

    def _log(self) -> None:
        for frame in itertools.cycle(["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]):
            if self.done:
                return

            print(f"\r{frame}  | [{self._file}] > {self._oper}",end=" "*15)
            sleep(0.5)

    def start(self):
        t = threading.Thread(target=self._log)
        t.start()

    def set_file(self, new_file) -> None:
        self._file = new_file
    
    def set_oper(self, new_oper) -> None:
        self._oper = new_oper