import argparse
import os
import pathlib

import yaml

APPS_DIR = "apps"

IGNORE_LIST = ["auxtel", "cluster-config", "eas", "hexapodsim", "maintel", "mtm1m3", "mtm2",
               "obssys", "ospl-config"]

def main(opts):
    if opts.update_m1m3:
        IGNORE_LIST.remove("mtm1m3")
    if opts.update_m2:
        IGNORE_LIST.remove("mtm2")

    if opts.dir_file is not None:
        with open(os.path.expanduser(opts.dir_file)) as ifile:
            dirs = [x.strip() for x in ifile.readlines()]
        use_dirs = True
    else:
        use_dirs = False

    print(f"Updating {opts.update_key} to {opts.update_value} for {opts.env} environment")
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

        if appdir.name == "kafka-producers" or appdir.name == "ospl-daemon":
            top_tag = appdir.name
        else:
            top_tag = "csc"

        for appfile in appdir.iterdir():
            if opts.env in appfile.name:
                print(f"Updating: {appfile}")

                values = None

                with open(appfile) as ifile:
                    values = yaml.safe_load(ifile)

                vtt = values[top_tag]
                keys = opts.update_key.split(".")
                for key in keys[:-1]:
                    vtt = vtt[key]

                vtt[keys[-1]] = opts.update_value

                if opts.debug and values is not None:
                    print(values)

                if values is None:
                    print(f"Problem reading {appfile}")
                else:
                    with open(appfile, 'w') as ofile:
                        yaml.dump(values, ofile, sort_keys=False)

if __name__ == '__main__':
    description = ["Update parameter for a given environment."]
    description.append("Run the script in the top-level argocd-csc directory.")
    description.append("Do not include the top-level section in key specification.")
    description.append("If the key does not appear in the files, it will be added.")
    parser = argparse.ArgumentParser(description=" ".join(description),
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("update_key", help="Key to update. Uses dot formatting for sections.")
    parser.add_argument("update_value", help="Value for key to update.")
    parser.add_argument("-e", "--env", dest="env", required=True,
                        help="Pass the environment to change.")
    parser.add_argument("-d", "--debug", dest="debug", action="store_true",
                        help="Print intermediate information")
    parser.add_argument("--update-m1m3", action="store_true", help="Allow M1M3 to be updated.")
    parser.add_argument("--update-m2", action="store_true", help="Allow M2 to be updated.")
    parser.add_argument("--dir-file", help="Provide a file with a list of directories to look at.")
    args = parser.parse_args()

    main(args)
