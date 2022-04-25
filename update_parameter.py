import argparse
import os
import pathlib

import yaml

APPS_DIR = "apps"

IGNORE_LIST = [
    "auxtel",
    "calsys",
    "cluster-config",
    "dmocps",
    "eas",
    "hexapodsim",
    "love",
    "maintel",
    "obssys",
    "ospl-config",
]

SAME_AS_DEPLOYMENT = [
    "kafka-producers",
    "love-frontend",
    "love-manager",
    "love-nginx",
    "love-producer",
    "ospl-daemon",
    "ospl-main-daemon",
]


def update_tag(values, top_key, update_key, update_value):
    tags = top_key.split(".")
    vtt = values[tags[0]]
    for tag in tags[1:]:
        vtt = vtt[tag]
    keys = update_key.split(".")
    try:
        for key in keys[:-1]:
            vtt = vtt[key]
    except KeyError:
        return

    vtt[keys[-1]] = update_value


def main(opts):
    if opts.ignore_non_ospl:
        IGNORE_LIST.extend(["love-frontend", "love-manager", "love-nginx"])

    if opts.dir_file is not None:
        with open(os.path.expanduser(opts.dir_file)) as ifile:
            dirs = [x.strip() for x in ifile.readlines()]
        use_dirs = True
    else:
        use_dirs = False

    print(
        f"Updating {opts.update_key} to {opts.update_value} for {opts.env} environment"
    )
    apps = pathlib.PosixPath(APPS_DIR)
    dirlist = list(apps.iterdir())
    for appdir in dirlist:
        if use_dirs:
            if appdir.name not in dirs:
                continue
        else:
            if appdir.name in IGNORE_LIST:
                continue

        if opts.debug:
            print(appdir)

        if appdir.name in SAME_AS_DEPLOYMENT:
            top_tag = appdir.name
        else:
            top_tag = "csc"

        for appfile in appdir.iterdir():
            if opts.env in appfile.name:
                print(f"Updating: {appfile}")

                values = None

                with open(appfile) as ifile:
                    values = yaml.safe_load(ifile)

                if top_tag != "love-nginx":
                    update_tag(values, top_tag, opts.update_key, opts.update_value)
                else:
                    update_tag(
                        values,
                        f"{top_tag}.initContainers.frontend",
                        opts.update_key,
                        opts.update_value,
                    )
                    update_tag(
                        values,
                        f"{top_tag}.initContainers.manager",
                        opts.update_key,
                        opts.update_value,
                    )

                if opts.debug and values is not None:
                    print(values)

                if values is None:
                    print(f"Problem reading {appfile}")
                else:
                    with open(appfile, "w") as ofile:
                        yaml.dump(values, ofile, sort_keys=False)


if __name__ == "__main__":
    description = ["Update parameter for a given environment."]
    description.append("Run the script in the top-level argocd-csc directory.")
    description.append("Do not include the top-level section in key specification.")
    description.append("If the key does not appear in the files, it will be added.")
    parser = argparse.ArgumentParser(
        description=" ".join(description),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "update_key", help="Key to update. Uses dot formatting for sections."
    )
    parser.add_argument("update_value", help="Value for key to update.")
    parser.add_argument(
        "-e", "--env", dest="env", required=True, help="Pass the environment to change."
    )
    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        help="Print intermediate information",
    )
    parser.add_argument(
        "--dir-file", help="Provide a file with a list of directories to look at."
    )
    parser.add_argument(
        "--ignore-non-ospl",
        action="store_true",
        help="Do not apply parameter to non-OSPL apps.",
    )
    args = parser.parse_args()

    main(args)
