import logging

logger = logging.getLogger('pyportlib')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s: in %(funcName)s',
                    )

log_format = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s: in %(funcName)s")

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(log_format)
logger.addHandler(consoleHandler)


