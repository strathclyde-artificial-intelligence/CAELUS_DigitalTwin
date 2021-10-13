
class Logger():
    def __init__(self, debug=False):
        self.__debug_mode = debug
        self.__disabled = False

    def set_disabled(self, disabled):
        assert disabled in [True, False]
        self.__disabled = disabled
    
    def set_debug(self, debug):
        assert debug in [True, False]
        self.__debug_mode = debug

    def __print(self, prefix, s):
        if self.__disabled:
            return
        print(f'{prefix} {s}')
                
    def debug(self, s):
        if self.__debug_mode:
            self.__print('[DEBUG]', s)

    def info(self, s):
        self.__print('[INFO]', s)

    def warn(self, s):
        self.__print('[WARNING]', s)

    def fatal(self, s):
        print(f'[FATAL] {s}')
        exit(-1)