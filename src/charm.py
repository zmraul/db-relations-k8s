#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Charm the service.

Refer to the following post for a quick-start guide that will help you
develop a new k8s charm using the Operator Framework:

    https://discourse.charmhub.io/t/4208
"""

import logging

from charms.redis_k8s.v0.redis import RedisRequires, RedisRelationCharmEvents
from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus, WaitingStatus
from redis import Redis, RedisError

logger = logging.getLogger(__name__)


class DBRelationK8sCharm(CharmBase):
    """Charm the service."""

    on = RedisRelationCharmEvents()
    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)

        self.framework.observe(self.on.start, self._on_start)

        ####################
        #### REDIS #########
        ####################
        # Charm library helper class
        self._stored.set_default(redis_relation={})
        self.redis = RedisRequires(self, self._stored)

        self.framework.observe(self.on.redis_relation_created, self._redis_relation_created)
        self.framework.observe(self.on.redis_relation_updated, self._redis_relation_updated)

    def _on_start(self, _) -> None:
        self.unit.status = BlockedStatus("Waiting relation to database")

    #### REDIS ####
    def _redis_relation_created(self, event):
        """"""
        logger.info("Redis application joined!")
        self.unit.status = WaitingStatus("Setting up relation")

        for relation in self.model.relations["redis"]:
            logger.info(f'RELATIONS CREATED: {relation.app.name}')
    
    def _redis_relation_updated(self, event):
        """Handler for custom relation updated event."""

        url = self.redis.get_url()
        data = self.redis.get_relation_data()
        if not data:
            logger.info("Relation being removed")
            return

        host = data.get("hostname")
        port = data.get("port")

        if not(host and port):
            logger.warning("Didn't get any data from relation, deferring")
            event.defer()
            return

        logger.info(f"From relation:\n\t- host {host}\n\t- port {port}\n\t- url {url}")

        # try to connect to Redis
        client = Redis(host=host, port=port)
        try:
            result = client.ping()
        except RedisError as e:
            logger.error(e)
            self.unit.status = BlockedStatus("Redis exception")
            return
        finally:
            client.close()

        if result:
            self.unit.status = ActiveStatus()
            logger.info(f"PONG obtained from {host}:{port} :)")
        else:
            msg = f"Redis database connection failed - {host}:{port}"
            self.unit.status = BlockedStatus(msg)
            logger.error(msg)
            event.defer()


if __name__ == "__main__":
    main(DBRelationK8sCharm)
