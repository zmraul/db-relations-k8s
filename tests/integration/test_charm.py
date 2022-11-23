#!/usr/bin/env python3

import logging

import pytest
from pytest_operator.plugin import OpsTest

logger = logging.getLogger(__name__)

APP_NAME = "status-charm"


@pytest.mark.abort_on_fail
async def test_build_and_deploy(ops_test: OpsTest):
    charm = await ops_test.build_charm(".")
    await ops_test.model.deploy(charm, application_name=APP_NAME)
    await ops_test.model.wait_for_idle(apps=[APP_NAME], timeout=50)

    assert ops_test.model.applications[APP_NAME].status == "waiting"
