
MAX_TIME = 1920     # 16 minutes
MIN_TIME = 30        # 30 seconds
ATTEMPT_LIMIT = 4

class Backoff_Timer:

    def __init__(self):
        self.__current_time = MIN_TIME
        self.__counter = 0

    def get_wait_time(self):
        self.__counter = self.__counter + 1
        if self.__current_time < MAX_TIME and self.__counter > ATTEMPT_LIMIT:
            self.__counter = 0
            self.__current_time = self.__current_time * 2
        return self.__current_time

    def reset_time(self):
        self.__current_time = MIN_TIME
        self.__counter = 0