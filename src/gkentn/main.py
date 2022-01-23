import os

from gkentn.core import Handler, Notifier

SLACK_WEBHOOK_URL_ENV = "SLACK_WEBHOOK_URL"


def main() -> None:
    if SLACK_WEBHOOK_URL_ENV not in os.environ:
        raise ValueError("No slack webhook url specified.")

    slack_webhook_url = os.environ[SLACK_WEBHOOK_URL_ENV]

    handler = Handler()
    notifier = Notifier(slack_webhook_url)

    handler.wait()  # wait for termination
    notifier.notify()  # notify


if __name__ == "__main__":
    main()
