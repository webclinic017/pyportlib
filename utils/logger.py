import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s: in %(funcName)s',
                    filename='utils/PortfolioCore.log',
                    filemode="w")

log_format = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s: in %(funcName)s")

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(log_format)
logger.addHandler(consoleHandler)


