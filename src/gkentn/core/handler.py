import datetime
import logging
import time
from dataclasses import dataclass
from typing import Optional

import requests

METADATA_URL = "http://metadata.google.internal/computeMetadata/v1/"
METADATA_HEADERS = {"Metadata-Flavor": "Google"}

PREEMPTIBLE_NODE_TERMINATION_DURATION = datetime.timedelta(seconds=30)
REGULAR_NODE_TERMINATION_DURATION = datetime.timedelta(hours=1)  # Defaults for GPU VMs


@dataclass
class State:
    instance_name: str
    zone: str
    project_id: str
    machine_type: str
    is_preemptible_node: bool
    termination_time: Optional[datetime.datetime]
    last_updated_at: datetime.datetime


class Handler:
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

        self._state: State

        self.logger.info("Checking instance type")
        self._check_instance()
        self.logger.info("Initializing handler state")
        self._initialize_state()

    def _check_instance(self) -> None:
        r = requests.get(METADATA_URL + "instance/scheduling/on-host-maintenance", headers=METADATA_HEADERS)
        r.raise_for_status()
        if r.text != "TERMINATE":
            raise ValueError("This instance does not need to handle termination")

    def _initialize_state(self) -> None:
        r = requests.get(METADATA_URL + "instance/name", headers=METADATA_HEADERS)
        r.raise_for_status()
        instance_name = r.text

        r = requests.get(METADATA_URL + "instance/zone", headers=METADATA_HEADERS)
        r.raise_for_status()
        zone = r.text.split("/")[-1]

        r = requests.get(METADATA_URL + "project/project-id", headers=METADATA_HEADERS)
        r.raise_for_status()
        project_id = r.text

        r = requests.get(METADATA_URL + "instance/machine-type", headers=METADATA_HEADERS)
        r.raise_for_status()
        machine_type = r.text.split("/")[-1]

        r = requests.get(METADATA_URL + "instance/scheduling/preemptible", headers=METADATA_HEADERS)
        r.raise_for_status()
        is_preemptible_node = r.text == "TRUE"

        self._state = State(
            instance_name=instance_name,
            zone=zone,
            project_id=project_id,
            machine_type=machine_type,
            is_preemptible_node=is_preemptible_node,
            termination_time=None,
            last_updated_at=datetime.datetime.now(),
        )

    def _store_pending_termination(self) -> None:
        termination_time = datetime.datetime.now()
        if self._state.is_preemptible_node:
            termination_time += PREEMPTIBLE_NODE_TERMINATION_DURATION
        else:
            termination_time += REGULAR_NODE_TERMINATION_DURATION
        self._state.termination_time = termination_time

    def _update_state(self) -> None:
        r = requests.get(METADATA_URL + "instance/maintenance-event", headers=METADATA_HEADERS)
        if r.status_code == 503:
            self.logger.warning("instance/maintenance-event return 503 status code")
            return
        r.raise_for_status()
        if r.text == "TERMINATE_ON_HOST_MAINTENANCE":
            self._store_pending_termination()

        r = requests.get(METADATA_URL + "instance/preempted", headers=METADATA_HEADERS)
        if r.status_code == 503:
            self.logger.warning("instance/preempted return 503 status code")
            return
        r.raise_for_status()
        if r.text == "TRUE":
            self._store_pending_termination()

        self._state.last_updated_at = datetime.datetime.now()

    def wait(self) -> State:
        while True:
            self._update_state()

            if self._state.termination_time is not None:
                self.logger.info("termination detected")
                return self._state

            if self._state.last_updated_at < datetime.datetime.now() - datetime.timedelta(seconds=60):
                raise TimeoutError(f"Failed to get maintenance status for node {self._state.instance_name}")

            time.sleep(5)
