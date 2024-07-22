# Script to install requirements. Use this if "pip install -r requirements.txt" doesn't work for some reason.
import subprocess
import os
from os.path import exists, join
from sys import exit

were_deps_installed = True

if not exists(join("logs", "install_reqs.log")):
    if not exists("logs"): os.mkdir("logs")
    open(join("logs", "install_reqs.log"), "x")
    were_deps_installed = False

if were_deps_installed:
    print("[Snazzle] [AutoDep] Dependencies already installed. If there were errors in the first run, running this again won't fix anything.")
else:
    try:
        subprocess.run(["pip", "install", "-r", "requirements.txt"]).check_returncode()
    except(subprocess.CalledProcessError):
        print("[Snazzle] [AutoDep] Option 1 failed, switching to backup...")
        with open("requirements.txt", "rt") as f:
            file = f.read()
            for requirement in file.splitlines():
                try:
                    proc = subprocess.run(["pip", "install", requirement], 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    proc.check_returncode()
                    if "Requirement already satisfied" in proc.stdout:
                        print(f"[Snazzle] [AutoDep] {requirement} already installed...")
                    else:
                        print(f"[Snazzle] [AutoDep] Installed {requirement}")
                except subprocess.CalledProcessError as err:
                    print(f"[Snazzle] [AutoDep] An error occurred trying to install {requirement}. See logs/install_reqs.log for details.")
                    with open("logs/install_reqs.log", "xt+") as log:
                        log.writelines(err.stderr) 
                    exit(1)