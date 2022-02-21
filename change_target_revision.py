import argparse
import asyncio
import json

import helpers as hp


def create_patch_command(app, patch):
    """
    Parameters
    ----------
    app : `str`
        The app to patch.
    patch : `dict`
        The patch dictionary containing the targetRevision change.

    Returns
    -------
    `list`
        The patch command to run.
    """
    cmd = [
        "argocd",
        "app",
        "patch",
        f"{app}",
        "--patch",
        f"{json.dumps(patch)}",
        "--type",
        "merge",
    ]
    return cmd


def create_list_command(app):
    """
    Parameters
    ----------
    app : `str`
        The app to list child apps.

    Returns
    -------
    `list`
        The list command to run.
    """
    cmd = [
        "argocd",
        "app",
        "list",
        "-l",
        f"argocd.argoproj.io/instance={app}",
        "-o",
        "name",
    ]
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
        output = hp.run_cmd(command, as_lines=True)
        # Last entry is empty so don't send.
        return output[:-1]


def port_forward_command(cmd):
    cmd.append("--port-forward")
    cmd.append("--port-forward-namespace")
    cmd.append("argocd")
    return cmd


async def main(opts):
    """
    Parameters
    ----------
    opts : `argparse.Namespace`
        The script command-line arguments and options.
    """
    if opts.list is not None:
        apps = opts.list.split(",")
    else:
        apps = hp.STANDALONE_APPS + hp.COLLECTOR_APPS

    patch_dict = {"spec": {"source": {"targetRevision": f"{opts.target_revision}"}}}

    procs = []
    for app in apps:
        run_cmd = create_patch_command(app, patch_dict)
        if opts.use_port_forward:
            run_cmd = port_forward_command(run_cmd)
        procs.append(hp.run_async_cmd(run_cmd, opts.no_run))
        if app in hp.COLLECTOR_APPS and not opts.no_run:
            run_cmd = create_list_command(app)
            if opts.use_port_forward:
                run_cmd = port_forward_command(run_cmd)
            child_apps = run_command(run_cmd, False)
            for child_app in child_apps:
                run_cmd = create_patch_command(child_app, patch_dict)
                if opts.use_port_forward:
                    run_cmd = port_forward_command(run_cmd)
                procs.append(hp.run_async_cmd(run_cmd, opts.no_run))

    await asyncio.gather(*procs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "target_revision",
        type=str,
        help="The git branch to set as the target revision.",
    )

    parser.add_argument(
        "--list",
        help="Provide a comma-delimited list of apps to change the targetRevision.",
    )

    parser.add_argument(
        "--no-run", action="store_true", help="Do not run the commands."
    )

    parser.add_argument(
        "-p",
        "--use-port-forward",
        action="store_true",
        help="Use port-forwarding in the command call.",
    )

    args = parser.parse_args()

    asyncio.run(main(args))
