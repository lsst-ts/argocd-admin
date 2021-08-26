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
    if app == "csc-cluster-config":
        app_dir = app.replace("csc-", "")
    else:
        app_dir = app

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
        "--revision",
        f"{conf.revision}",
        "--path",
        f"apps/{app_dir}",
        "--values",
        f"values-{conf.env}.yaml",
    ]
    if conf.use_port_forward:
        cmd.append("--port-forward")
        cmd.append("--port-forward-namespace")
        cmd.append("argocd")

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
    apps = hp.STANDALONE_APPS + hp.COLLECTOR_APPS
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

    parser.add_argument(
        "--revision",
        default="HEAD",
        help="Provide the git branch against which the app will be created. Default is HEAD.",
    )

    parser.add_argument(
        "-p",
        "--use-port-forward",
        action="store_true",
        help="Use port-forwarding in the command call.",
    )

    args = parser.parse_args()

    main(args)
