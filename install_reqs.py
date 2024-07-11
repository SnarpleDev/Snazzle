# Script to install requirements. Use this if "pip install -r requirements.txt" doesn't work for some reason.
import subprocess

try:
    subprocess.run(["pip", "install", "-r", "requirements.txt"]).check_returncode()
except(subprocess.CalledProcessError):
    print("Option 1 failed, switching to backup...")
    with open("requirements.txt", "rt") as f:
        file = f.read()
        for requirement in file.splitlines():
            try:
                subprocess.run(["pip", "install", requirement]).check_returncode()
            except(subprocess.CalledProcessError):
                print(f"An error occurred trying to install {requirement}. See above for details.")
                break