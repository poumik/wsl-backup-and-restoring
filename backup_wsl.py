from pathlib import Path
from datetime import datetime
import subprocess
import sys

# Change this if your distribution has a different name.
# Check the name with: wsl --list --verbose
DISTRO_NAME = "Ubuntu"

# Backup location on the E: USB-SSD drive.
BACKUP_FOLDER = Path(r"E:\WSL-Backups")

# Create a timestamped backup filename.
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
backup_file = BACKUP_FOLDER / f"{DISTRO_NAME}-backup-{timestamp}.tar"


def run_command(command):
    print("Running:", " ".join(str(item) for item in command))
    subprocess.run(command, check=True)


def main():
    print(f"WSL distribution: {DISTRO_NAME}")
    print(f"Backup location: {backup_file}")
    print()

    # Confirm that the E: drive is available.
    if not Path("E:\\").exists():
        print("Error: The E: drive was not found.")
        print("Connect or mount the USB-SSD and try again.")
        sys.exit(1)

    # Create the backup folder if it does not already exist.
    BACKUP_FOLDER.mkdir(parents=True, exist_ok=True)

    # Confirm that the selected WSL distribution exists.
    result = subprocess.run(
        ["wsl.exe", "--list", "--quiet"],
        capture_output=True,
        text=True,
        errors="replace",
    )

    if result.returncode != 0:
        print("Error: Could not list WSL distributions.")
        sys.exit(1)

    installed_distributions = result.stdout.lower()

    if DISTRO_NAME.lower() not in installed_distributions:
        print(f"Error: WSL distribution '{DISTRO_NAME}' was not found.")
        print()
        print("Run this command to see the installed distributions:")
        print("wsl --list --verbose")
        sys.exit(1)

    # Stop WSL before creating the backup.
    print("Stopping WSL...")
    run_command(["wsl.exe", "--shutdown"])

    print()
    print("Creating backup...")
    print("This may take several minutes.")
    print()

    # Export the complete WSL distribution to the E: drive.
    run_command(
        [
            "wsl.exe",
            "--export",
            DISTRO_NAME,
            str(backup_file),
        ]
    )

    print()

    # Verify that the backup file exists and is not empty.
    if not backup_file.exists():
        print("Error: The backup file was not created.")
        sys.exit(1)

    backup_size = backup_file.stat().st_size

    if backup_size == 0:
        print("Error: The backup file is empty.")
        sys.exit(1)

    backup_size_gb = backup_size / (1024 ** 3)

    print("Backup completed successfully.")
    print(f"Backup file: {backup_file}")
    print(f"Backup size: {backup_size_gb:.2f} GB")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        print()
        print("The backup failed.")
        print(f"Command returned exit code: {error.returncode}")
        sys.exit(error.returncode)
    except KeyboardInterrupt:
        print()
        print("Backup cancelled.")
        sys.exit(1)
