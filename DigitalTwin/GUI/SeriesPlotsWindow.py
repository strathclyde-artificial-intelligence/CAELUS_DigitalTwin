from math import sin
from queue import Empty
import threading

class SeriesPlotsWindow():
    def __init__(self, dpg):
        self.__dpg = dpg
        self.__setup_window()
        self.__series = []
        self.__datapoints = {}

    def __setup_window(self):
        self.__t = 0
        self.window_name = 'PlotsWindow'
        self.__dpg.add_window(label=self.window_name, tag=self.window_name)

    def add_time_series(self, series_name, series_stream):
        name = f'{series_name}.plot'
        self.__series.append((series_name, series_stream))
        self.__dpg.add_plot(label=series_name, parent=self.window_name, height=300, width=-1, tag=name)
        self.__dpg.add_plot_legend(parent=name)
        self.__dpg.add_plot_axis(self.__dpg.mvXAxis, label="x", parent=name)
        self.__dpg.add_plot_axis(self.__dpg.mvYAxis, label="y", id=f"{name}.yaxis", parent=name)
        self.__dpg.add_line_series([], [], label=series_name, parent=f'{name}.yaxis', tag=f'{name}.series')
        self.__datapoints[series_name] = ([], [])

    def update(self):
        for ts_name, queue in self.__series:
            try:
                xs, ys = self.__datapoints[ts_name]
                val = queue.get(block=False)
                xs.append(len(xs) / 1000)
                ys.append(val)
                xs = xs[-1000:]
                ys = ys[-1000:]
                self.__dpg.set_value(f'{ts_name}.plot.series', [xs, ys])
            except Empty as _:
                pass
            except Exception as e:
                print(e)