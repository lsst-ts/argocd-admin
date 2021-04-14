import argparse
import pathlib

import yaml

APPS_DIR = "apps"


def main(opts):
    print(f"Updating apps using csc Helm chart to version {opts.chart_version}")
    apps = pathlib.PosixPath(APPS_DIR)
    dirlist = list(apps.iterdir())
    for appdir in dirlist:
        chart = appdir / "Chart.yaml"

        with chart.open() as ifile:
            values = yaml.safe_load(ifile)

        try:
            dependencies = values["dependencies"]
        except KeyError:
            continue
        for dependency in dependencies:
            if dependency["name"] == "csc":
                dependency["version"] = opts.chart_version

        # print(appdir, values)

        with chart.open("w") as ofile:
            yaml.dump(values, ofile, sort_keys=False)


if __name__ == "__main__":
    description = ["Update version for apps using the csc Helm chart"]
    parser = argparse.ArgumentParser(
        description=" ".join(description),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "chart_version", help="The version of the csc Helm chart to set."
    )
    args = parser.parse_args()
    main(args)
