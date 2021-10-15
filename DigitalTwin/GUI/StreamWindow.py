from io import SEEK_CUR
import logging
import threading
from collections import deque
import os

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
        self.__text_updated = False
        self.__read_so_far = 0
        self.__logger = logging.getLogger(__name__)

    def __update_text(self):
        while not self.__should_stop and self.__stream.readable():
            try:
                new_data = self.__stream.readline()
                self.__text_updated = True
                self.__deque.append(new_data.decode('utf-8'))
                curr_text = ''.join(self.__deque)
                self.__stream_text = curr_text
            except Exception as e: 
                print(e)
                self.__should_stop = True
        self.__logger.info(f'Stream window thread ({self.stream_window}) stopped')

    def __setup_window(self, window_name):
        self.stream_window = window_name
        self.stream_text_tag = f'{window_name}.Text'
        with self.__dpg.window(label=window_name, tag=self.stream_window):
            self.__dpg.add_text('', tag=self.stream_text_tag)
        
    def update(self):
        
        if self.__stream is None:
            return

        if not self.__initialised:
            self.__logger.info(f'Initialising stream read thread for {self.stream_window}')
            self.__read_thread = threading.Thread(target=self.__update_text)
            self.__read_thread.name = f'StreamWindow({self.stream_window})'
            self.__read_thread.daemon = True
            self.__read_thread.start()
            self.__initialised = True

        if self.__text_updated:
            self.__dpg.set_value(self.stream_text_tag, self.__stream_text)
            self.__text_updated = False
        y_max = self.__dpg.get_y_scroll_max(self.stream_window)
        self.__dpg.set_y_scroll(self.stream_window, y_max)

    def exit(self):
        self.__logger.info(f'Stream window for {self.stream_window} is exiting its read thread.')
        self.__should_stop = True
        self.__text_updated = True
        self.__stream_text = ''
        self.__stream = None

    def set_stream(self, stream):
        if stream is None:
            self.__logger.warn('Setting a None stream may result in undefined behavior.')
        self.__initialised = False
        self.__should_stop = False
        self.__stream = stream