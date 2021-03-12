import argparse
import asyncio

import helpers as hp


def run_command(command, do_run):
    print(f"{' '.join(command)}")
    if not do_run:
        output = hp.run_cmd(command)
        print(output)


def main(opts):
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
        cmd = base_cmd + ["-l", f"app.kubernetes.io/instance={app}", "--async"]
        run_command(cmd, opts.no_run)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--no-run", action="store_true", help="Do not run the commands.")

    args = parser.parse_args()

    main(args)
