#!/usr/bin/env python3

import logging
import os
import subprocess

logger = logging.getLogger(__name__)


def run_cmd(command: str, args: str = None):
    """Run command.

    Arg:
        command: can contain arguments
        args: command line arguments
    """
    if args is not None:
        command = f"{command} {args}"

    logger.debug(f"Executing command: {command}")

    output = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True,
        encoding="utf-8",
        timeout=15,
        env=os.environ,
    )

    logger.debug(f"{command}:\n{output.stdout}")

    if output.returncode != 0:
        msg = f"{command}:\n Stderr: {output.stderr}\n Stdout: {output.stdout}"
        logger.error(msg)
        raise Exception(msg)
