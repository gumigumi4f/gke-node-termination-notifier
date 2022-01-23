import os

from gkentn.core import Handler, Notifier
from gkentn.utils.logger import get_logger

SLACK_WEBHOOK_URL_ENV = "SLACK_WEBHOOK_URL"

logger = get_logger()


def main() -> None:
    if SLACK_WEBHOOK_URL_ENV not in os.environ:
        raise ValueError("No slack webhook url specified.")

    slack_webhook_url = os.environ[SLACK_WEBHOOK_URL_ENV]

    handler = Handler(logger)
    notifier = Notifier(slack_webhook_url, logger)

    state = handler.wait()  # wait for termination
    notifier.notify(state)  # notify


if __name__ == "__main__":
    main()
