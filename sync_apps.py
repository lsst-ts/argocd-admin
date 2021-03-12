import argparse
import asyncio

import helpers as hp


def run_command(command, no_run):
    """

    Parameters
    ----------
    command : `list`
        The command to run.
    no_run : `bool`
        Flag for deciding if to run the command.
    """
    print(f"{' '.join(command)}")
    if not no_run:
        output = hp.run_cmd(command)
        print(output)


async def main(opts):
    base_cmd = ["argocd", "app", "sync"]

    for app in hp.APPS:
        cmd = base_cmd + [app]
        run_command(cmd, opts.no_run)
        if app in ["ospl-daemon", "kafka-producers", "obssys"]:
            if app == "obssys":
                cmd = base_cmd + ["-l", f"app.kubernetes.io/instance={app}"]
                run_command(cmd, opts.no_run)
            print(f"When the {app} are running, type go to continue.")
            choice = ""
            while choice != "go":
                choice = input("Ready?:")

    for app in hp.ASYNC_APPS:
        cmd = base_cmd + [app]
        run_command(cmd, opts.no_run)

    procs = []
    for app in hp.ASYNC_APPS:
        cmd = base_cmd + ["-l", f"app.kubernetes.io/instance={app}"]
        procs.append(hp.run_async_cmd(cmd, opts.no_run))
    await asyncio.gather(*procs)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--no-run", action="store_true", help="Do not run the commands.")

    args = parser.parse_args()

    asyncio.run(main(args))
