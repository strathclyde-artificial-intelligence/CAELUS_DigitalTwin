from .ThreadMonitor import ThreadMonitor
import dearpygui.dearpygui as dpg
import logging 

class GUI():
    def __init__(self, logger=logging.getLogger(__name__)):
        self.__setup_gui()
        self.__sub_windows = []
        self.__logger = logger

    def __setup_gui(self):
        dpg.create_context()
        dpg.create_viewport(title='Digital Twin Monitor')
        dpg.setup_dearpygui()
        dpg.show_viewport()

    def __create_sub_windows(self):
        self.__sub_windows.append(ThreadMonitor(dpg))

    def start(self):
        self.__logger.info('Initialising GUI')
        self.__logger.info('Creating GUI Subwindows')
        self.__create_sub_windows()
        try:
            while dpg.is_dearpygui_running():
                for w in self.__sub_windows:
                    w.update()
                dpg.render_dearpygui_frame()
        except Exception as e:
            raise e
        finally:
            dpg.destroy_context()    