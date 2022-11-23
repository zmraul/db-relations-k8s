#!/usr/bin/env python3

"""Charm the service."""

import logging

from charms.operator_libs_linux.v1 import snap
from charms.operator_libs_linux.v1.snap import SnapError
from charms.prometheus_k8s.v0.prometheus_scrape import MetricsEndpointProvider
from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus

from utils import run_cmd

logger = logging.getLogger(__name__)


class StatusCharm(CharmBase):
    """Charm the service."""

    def __init__(self, *args):
        super().__init__(*args)

        self.metrics_endpoint = MetricsEndpointProvider(
            self,
            jobs=[
                {
                    "static_configs": [
                        {
                            "targets": ["*:9100"],
                        }
                    ]
                }
            ],
        )

        self.framework.observe(self.on.install, self._on_install)

    def _on_install(self, _) -> None:
        """Install things."""
        cache = snap.SnapCache()
        self.node_exporter = cache["node-exporter"]

        if self.node_exporter.present:
            return

        try:
            self.node_exporter.ensure(snap.SnapState.Latest, channel="edge")
        except SnapError as e:
            msg = f"Failed to install node-exporter. \n{e}"
            logger.error(msg)
            self.unit.status = BlockedStatus(msg)
            raise

        plugs = [
            "hardware-observe",
            "network-observe",
            "mount-observe",
            "system-observe",
        ]
        for plug in plugs:
            run_cmd(command=f"snap connect node-exporter:{plug}")
        
        self.unit.status = ActiveStatus()


if __name__ == "__main__":
    main(StatusCharm)
