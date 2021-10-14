from .ThreadMonitor import ThreadMonitor
from .StreamWindow import StreamWindow
from ..Interfaces.StreamHandler import StreamHandler
import dearpygui.dearpygui as dpg
import logging 

class GUI(StreamHandler):
    def __init__(self, logger=logging.getLogger(__name__)):
        self.__setup_gui()
        self.__sub_windows = {}
        self.__logger = logger

    def __setup_gui(self):
        dpg.create_context()
        dpg.create_viewport(title='Digital Twin Monitor')
        dpg.setup_dearpygui()
        dpg.show_viewport()

    def __create_sub_windows(self):
        self.__sub_windows['thread_monitor'] = ThreadMonitor(dpg)
        dpg.show_documentation()

    def start(self):
        self.__logger.info('Initialising GUI')
        self.__logger.info('Creating GUI Subwindows')
        self.__create_sub_windows()
        try:
            while dpg.is_dearpygui_running():
                for w_name, w in self.__sub_windows.items():
                    w.update()
                dpg.render_dearpygui_frame()
        except Exception as e:
            raise e
        finally:
            dpg.destroy_context()    
    
    def new_stream_available(self, stream_name, stream):
        self.__logger.info(f'GUI module has received a new stream: {stream_name}')
        self.__sub_windows[f'stream_{stream_name}'] = StreamWindow(dpg, stream_name, stream)

    def invalidate_stream(self, stream_name):
        self.__logger.info(f'Stream invalidation request received for {stream_name}')
        self.__sub_windows[f'stream_{stream_name}'].exit()
        del self.__sub_windows[f'stream_{stream_name}']