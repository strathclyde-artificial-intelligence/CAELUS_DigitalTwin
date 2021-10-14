import logging
import threading
from collections import deque

class StreamWindow():
    def __init__(self, dpg, name, stream, max_buff_size = 1024):
        self.__dpg = dpg
        self.__stream = stream
        self.__setup_window(name)
        self.__deque = deque([], max_buff_size)
        self.__read_thread = None
        self.__should_stop = False
        self.__initialised = False
        self.__stream_text = ''
        self.__logger = logging.getLogger(__name__)

    def __update_text(self):
        while not self.__should_stop:
            try:
                new_line = self.__stream.readline()
                self.__deque.append(new_line.decode('utf-8'))
                curr_text = '\n'.join(self.__deque)
                self.__stream_text = curr_text
            except Exception as e: 
                print(e)
                self.__should_stop = True

    def __setup_window(self, window_name):
        self.stream_window = window_name
        self.stream_text_tag = f'{window_name}.Text'
        with self.__dpg.window(label=window_name, tag=self.stream_window):
            self.__dpg.add_text('', tag=self.stream_text_tag)
        
    def update(self):
        if not self.__initialised:
            self.__logger.info(f'Initialising stream read thread for {self.stream_window}')
            self.__read_thread = threading.Thread(target=self.__update_text)
            self.__read_thread.name = f'StreamWindow({self.stream_window})'
            self.__read_thread.daemon = True
            self.__read_thread.start()
            self.__initialised = True
        self.__dpg.set_value(self.stream_text_tag, self.__stream_text)
    def exit(self):
        self.__should_stop = True