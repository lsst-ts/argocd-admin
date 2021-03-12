import asyncio
import os
import subprocess as sp

__all__ = [
    "APPS",
    "ASYNC_APPS",
    "run_async_cmd",
    "run_cmd",
]

APPS = [
    "csc-cluster-config",
    "ospl-config",
    "ospl-daemon",
    "kafka-producers",
    "obssys"
]

ASYNC_APPS = [
    "auxtel",
    "eas",
    "maintel"
]


async def run_async_cmd(command):
    pass


def run_cmd(command, as_lines=False):
    """Run a command via subprocess::run.

    Parameters
    ----------
    command : list
        The command to run.
    as_lines : bool, optional
        Return the output as a list instead of a string.

    Returns
    -------
    str or list
        The output from the command.
    """
    output = sp.run(command, stdout=sp.PIPE, stderr=sp.STDOUT)
    decoded_output = output.stdout.decode("utf-8")
    if as_lines:
        return decoded_output.split(os.linesep)
    else:
        return decoded_output[:-1]
