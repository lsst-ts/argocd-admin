import asyncio
import os
import subprocess as sp

__all__ = [
    "APPS",
    "ASYNC_APPS",
    "COLLECTOR_APPS",
    "SINGLE_APPS",
    "STANDALONE_APPS",
    "run_async_cmd",
    "run_cmd",
]

APPS = [
    "csc-cluster-config",
    "ospl-config",
    "ospl-daemon",
    "kafka-producers",
    "obssys",
]

ASYNC_APPS = ["auxtel", "dmocps", "eas", "love", "maintel"]


STANDALONE_APPS = [
    "csc-cluster-config",
    "ospl-config",
    "ospl-daemon",
    "kafka-producers",
]

SINGLE_APPS = ["test42"]

COLLECTOR_APPS = ["auxtel", "dmocps", "eas", "love", "maintel", "obssys"]


async def run_async_cmd(command, no_run):
    """Run a command asynchronously.

    Parameters
    ----------
    command : `list`
        The command to run.
    no_run : `bool`
        Flag for deciding if to run the command.
    """
    cmd = " ".join(command)
    print(cmd)
    if not no_run:
        proc = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
        )

        stdout = await proc.communicate()
        print(stdout[0].decode("utf-8"))
    else:
        await asyncio.sleep(0)


def run_cmd(command, as_lines=False):
    """Run a command via subprocess::run.

    Parameters
    ----------
    command : `list`
        The command to run.
    as_lines : `bool`, optional
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
