from DigitalTwin.ExitHandler import ExitHandler
from DigitalTwin.Interfaces.MissionManager import MissionManager
from DigitalTwin.Interfaces.SimulationStack import SimulationStack
from .ThreadMonitor import ThreadMonitor
from .StreamWindow import StreamWindow
from .SeriesPlotsWindow import SeriesPlotsWindow
from ..Interfaces.StreamHandler import StreamHandler
from ..Interfaces.TimeSeriesHandler import TimeSeriesHandler
from ..Interfaces.SimulationStack import SimulationStack
import dearpygui.dearpygui as dpg
import logging 
import signal
from DigitalTwin.error_codes import OK, JSON_READ_EC

class GUI(StreamHandler, TimeSeriesHandler):
    DEFAULT_GUI_INIT_FILE_NAME = 'gui_layout.ini'

    def __init__(self, init_file=None, logger=logging.getLogger(__name__)):
        # Save config file (Window position is maintained across sessions)
        self.__init_file = init_file
        self.__setup_gui()
        self.__sub_windows = {}
        self.__logger = logger
        self.__mission_manager = None
        self.__sim_stack = None
        self.__should_stop = False

    def __setup_gui(self):
        dpg.create_context()
        dpg.create_viewport(title='Digital Twin Monitor', height=1080, width=1920, x_pos=0, y_pos=0)
        dpg.setup_dearpygui()
        if self.__init_file is not None:
            dpg.configure_app(init_file=self.__init_file)
        dpg.show_viewport()

    def __create_sub_windows(self):
        self.__sub_windows['thread_monitor'] = ThreadMonitor(dpg)
        self.__sub_windows['series_plot_window'] = SeriesPlotsWindow(dpg)

    def start(self):
        signal.signal(signal.SIGINT, lambda _,__: self.cleanup())
        self.__logger.info('Initialising GUI')
        self.__logger.info('Creating GUI Subwindows')
        self.__create_sub_windows()
        exit_handler = ExitHandler.shared()
        try:
            while dpg.is_dearpygui_running() and not self.__should_stop and not exit_handler.should_exit():
                for w_name, w in [a for a in self.__sub_windows.items()]:
                    w.update()
                dpg.render_dearpygui_frame()
        except Exception as e:
            self.__logger.warn(e)
        finally:
            self.__logger.info("DearPyGUI exiting")
            dpg.stop_dearpygui()

    def cleanup(self):
        exit_handler = ExitHandler.shared()
        self.__should_stop = True
        dpg.save_init_file(GUI.DEFAULT_GUI_INIT_FILE_NAME)    
        exit_handler.issue_exit_with_code_and_message(OK, None)

    def new_stream_available(self, stream_name, stream):
        self.__logger.info(f'GUI module has received a new stream: {stream_name}')
        name = f'stream_{stream_name}'
        if name not in self.__sub_windows:
            self.__sub_windows[name] = StreamWindow(dpg, stream_name, stream)
        else:
            self.__sub_windows[name].set_stream(stream)

    def invalidate_stream(self, stream_name):
        self.__logger.info(f'Stream invalidation request received for {stream_name}')
        name = f'stream_{stream_name}'
        if name in self.__sub_windows:
            self.__sub_windows[name].exit()

    def set_mission_manager(self, mission_manager:MissionManager):
        self.__mission_manager = mission_manager

    def set_simulation_stack(self, sim_stack: SimulationStack):
        self.__sim_stack = sim_stack

    def new_time_series_stream_available(self, name, stream):
        if 'series_plot_window' not in self.__sub_windows:
            self.__logger.warn('Tried to add a time series plot but no window is present to display it.')
        else:
            self.__sub_windows['series_plot_window'].add_time_series(name, stream)
        