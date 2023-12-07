from altmo_rideschool import rideschool_app
import logging

if __name__ == "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    rideschool_app.logger.handlers = gunicorn_logger.handlers
    rideschool_app.logger.setLevel(gunicorn_logger.level)
    rideschool_app.run()
