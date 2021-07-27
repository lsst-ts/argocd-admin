import argparse
import os

import helpers as hp


def create_command(app, conf):
    """Create the app creation command.

    Parameters
    ----------
    app : `str`
        The name of the app to create.
    conf : `SimpleNamespace`
        The options for the app.

    Returns
    -------
    `list` of `str`
        The assembled command line to run.
    """
    cmd = [
        "argocd",
        "app",
        "create",
        f"{app}",
        "--dest-namespace",
        "argocd",
        "--dest-server",
        "https://kubernetes.default.svc",
        "--repo",
        "https://github.com/lsst-ts/argocd-csc.git",
        "--path",
        "",
    ]
    if app == "csc-cluster-config":
        app = app.replace("csc-", "")
    cmd[11] = f"apps/{app}"
    cmd.append("--values")
    cmd.append(f"values-{conf.env}.yaml")
    return cmd


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


def main(opts):

    if opts.list is not None:
        apps = opts.list.split(",")
    else:
        apps = hp.STANDALONE_APPS + hp.COLLECTOR_APPS

    for app in apps:
        run_cmd = create_command(app, opts)
        run_command(run_cmd, opts.no_run)


if __name__ == "__main__":
    description = ["Create argocd app. The current apps are:"]
    apps = hp.APPS + hp.ASYNC_APPS
    for app in apps:
        description.append(f"   {app}")
    parser = argparse.ArgumentParser(
        description=os.linesep.join(description),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--no-run", action="store_true", help="Do not run the commands."
    )
    parser.add_argument(
        "env", help="Provide the environment for the Helm values files."
    )
    parser.add_argument(
        "--list", help="Provide a comma-delimited list of apps to create."
    )

    args = parser.parse_args()

    main(args)
