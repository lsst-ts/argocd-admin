import helpers as hp

def main():
    base_cmd = ["argocd", "app", "sync"]

    for app in hp.APPS:
        cmd = base_cmd + [app]
        print(f"{' '.join(cmd)}")
        output = hp.run_cmd(cmd)
        print(output)
        if app == "kafka-producers":
            print("When the kafka-producers are running, type go to continue.")
            choice = ""
            while choice != "go":
                choice = input("Ready?:")

    for app in hp.ASYNC_APPS:
        cmd = base_cmd + [app, "--async"]
        print(f"{' '.join(cmd)}")
        output = hp.run_cmd(cmd)
        print(output)

if __name__ == '__main__':
    main()
