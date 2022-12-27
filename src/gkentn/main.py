import os
import time

from gkentn.core import Handler, Notifier
from gkentn.utils.logger import get_logger

SLACK_WEBHOOK_URL_ENV = "SLACK_WEBHOOK_URL"

logger = get_logger()


def main() -> None:
    if SLACK_WEBHOOK_URL_ENV not in os.environ:
        raise ValueError("No slack webhook url specified.")

    slack_webhook_url = os.environ[SLACK_WEBHOOK_URL_ENV]

    logger.info("Initialize handler")
    handler = Handler(logger)
    logger.info("Initialize notifier")
    notifier = Notifier(slack_webhook_url, logger)

    logger.info("Wait for termination")
    state = handler.wait()  # wait for termination
    logger.info("Notify termination")
    notifier.notify(state)  # notify

    while True:
        time.sleep(1000)


if __name__ == "__main__":
    main()
