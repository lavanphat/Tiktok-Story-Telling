from logging import basicConfig, getLogger, DEBUG

class Logger:
    def __init__(self) -> None:
        basicConfig(format='%(asctime)s %(levelname)s | %(message)s', datefmt='%H:%M:%S')
        self.__logger = getLogger()
        self.__logger.setLevel(DEBUG)

    def error(self, text: str):
        self.__logger.error(f"{text}")
    
    def info(self, text: str):
        self.__logger.info(f"{text}")
