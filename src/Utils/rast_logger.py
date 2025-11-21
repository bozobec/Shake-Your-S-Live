import logging


def get_default_logger():
    """
    Return as logging Logger. Makes sure all files get the same logger.
    Uses ascitime, filename and message
    :return: A logging logger that uses ascitime, filename and message
    """
    # This makes the logger show anything above log-level Info. Debug level gets discarded.
    format = '%(asctime)s ~ %(filename)s   %(message)s'
    logging.basicConfig(level=logging.INFO, format=format)
    return logging.getLogger("Rast")
