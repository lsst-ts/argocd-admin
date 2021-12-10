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
    apps_to_sync = hp.APPS
    async_apps_to_sync = hp.ASYNC_APPS
    if opts.no_sync is not None:
        remove_apps = opts.no_sync.split(",")
        for remove_app in remove_apps:
            try:
                del apps_to_sync[apps_to_sync.index(remove_app)]
            except ValueError:
                pass
            try:
                del async_apps_to_sync[async_apps_to_sync.index(remove_app)]
            except ValueError:
                pass

    base_cmd = ["argocd", "app", "sync"]
    if opts.use_port_forward:
        base_cmd.extend(["--port-forward", "--port-forward-namespace", "argocd"])

    if opts.one is None:
        for app in apps_to_sync:
            cmd = base_cmd + [app]
            run_command(cmd, opts.no_run)
            if app in ["ospl-daemon", "kafka-producers", "obssys"]:
                if app == "obssys":
                    cmd = base_cmd + ["-l", f"argocd.argoproj.io/instance={app}"]
                    run_command(cmd, opts.no_run)
                print(f"When the {app} are running, type go to continue.")
                choice = ""
                while choice != "go":
                    choice = input("Ready?:")

        for app in async_apps_to_sync + hp.SINGLE_APPS:
            cmd = base_cmd + [app]
            run_command(cmd, opts.no_run)

        procs = []
        for app in async_apps_to_sync:
            cmd = base_cmd + ["-l", f"argocd.argoproj.io/instance={app}"]
            procs.append(hp.run_async_cmd(cmd, opts.no_run))
        await asyncio.gather(*procs)
    else:
        app = opts.one
        if opts.instance:
            cmd = base_cmd + ["-l", f"argocd.argoproj.io/instance={app}"]
        else:
            cmd = base_cmd + [app]
        run_command(cmd, opts.no_run)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--no-run", action="store_true", help="Do not run the commands."
    )
    parser.add_argument("--one", help="Sync one app.")
    parser.add_argument(
        "--instance",
        action="store_true",
        help="Sync the apps belonging to a top-level app.",
    )
    parser.add_argument("--no-sync", help="List (comma-delimited) of apps not to sync.")

    parser.add_argument(
        "-p",
        "--use-port-forward",
        action="store_true",
        help="Use port-forwarding in the command call.",
    )

    args = parser.parse_args()

    asyncio.run(main(args))
