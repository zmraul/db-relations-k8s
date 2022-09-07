#!/usr/bin/env python3

import logging

from ops.charm import CharmBase
from ops.main import main
from ops.model import BlockedStatus

logger = logging.getLogger(__name__)


class EzCharm(CharmBase):
    """Charm the service."""

    def __init__(self, *args):
        super().__init__(*args)

        self.framework.observe(self.on.start, self._on_start)

    def _on_start(self, _) -> None:
        self.unit.status = BlockedStatus("Waiting on stuff")


if __name__ == "__main__":
    main(EzCharm)
