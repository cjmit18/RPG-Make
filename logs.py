import logging
class logging:
    """
    Custom logging class to handle logging setup and configuration.
    """
    @staticmethod
    def setup_logging():
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('game.log', mode='w')
            ]
        )
        log = logging.getLogger(__name__)
        log.info("Logging setup complete.")
        return log