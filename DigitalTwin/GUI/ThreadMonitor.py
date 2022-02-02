import threading 

class ThreadMonitor():
    def __init__(self, dpg):
        super().__init__()
        self.__threads = []
        self.__dpg = dpg
        self.setup_thread_monitor_window()

    def setup_thread_monitor_window(self):
        self.thread_monitor_window = 'ThreadMonitor'
        self.thread_monitor_table = f'{self.thread_monitor_window}.Table' 

        with self.__dpg.window(label=self.thread_monitor_window, tag=self.thread_monitor_window):
            with self.__dpg.table(header_row=True, tag=self.thread_monitor_table):
                self.__dpg.add_table_column(label='Thread Name')

    def update(self):
        current_threads = [f'{t.name}' + (' (Daemon)' if t.daemon else '') for t in threading.enumerate()]
        to_delete = set(self.__threads).difference(set(current_threads))
        to_add =  set(current_threads).difference(set(self.__threads))
        self.__threads = current_threads
        main_t_name = threading.main_thread().name

        for t in to_delete:
            row_name = f'{self.thread_monitor_table}.{t}'
            self.__dpg.delete_item(row_name)

        for t in to_add:
            t = t if t != main_t_name else f'{t} (Main thread)'
            row_name = f'{self.thread_monitor_table}.{t}'
            self.__dpg.add_table_row(parent=self.thread_monitor_table, tag=row_name)
            self.__dpg.add_text(t, parent=row_name)
