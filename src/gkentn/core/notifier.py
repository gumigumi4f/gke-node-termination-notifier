import logging

from slack_sdk.webhook import WebhookClient

from gkentn.core.handler import State


class Notifier:
    def __init__(self, slack_webhook_url: str, logger: logging.Logger) -> None:
        self.logger = logger

        self.slack_webhook_url = slack_webhook_url

    def notify(self, state: State) -> None:
        if state.termination_time is None:
            raise ValueError("termination time is None")

        self.logger.info("Notifying instance state to slack")

        webhook = WebhookClient(self.slack_webhook_url)
        webhook.send(
            attachments=[
                {
                    "color": "warning",
                    "title": ":warning: Node Termination",
                    "fields": [
                        {
                            "title": "InstanceName",
                            "value": state.instance_name,
                            "short": False,
                        },
                        {
                            "title": "MachineType",
                            "value": state.machine_type,
                            "short": False,
                        },
                        {
                            "title": "Zone",
                            "value": state.zone,
                            "short": True,
                        },
                        {
                            "title": "ProjectID",
                            "value": state.project_id,
                            "short": True,
                        },
                        {
                            "title": "Termination Time",
                            "value": state.termination_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "short": True,
                        },
                        {
                            "title": "Is Preemptible Node",
                            "value": str(state.is_preemptible_node).lower(),
                            "short": True,
                        },
                    ],
                }
            ]
        )
