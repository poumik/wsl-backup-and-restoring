import argparse
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Defaults. Override them on the command line instead of editing this file:
#   python backup_wsl.py --distro Debian --backup-root D:\WSL-Backups
# Check the distribution name with: wsl --list --verbose
DEFAULT_DISTRO = "Ubuntu-24.04"
DEFAULT_BACKUP_ROOT = Path(r"E:\WSL-Backups")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Back up a WSL distribution to a .tar file using wsl --export."
    )
    parser.add_argument(
        "--distro",
        default=DEFAULT_DISTRO,
        help=f"WSL distribution name, exactly as shown by 'wsl --list' (default: {DEFAULT_DISTRO})",
    )
    parser.add_argument(
        "--backup-root",
        type=Path,
        default=DEFAULT_BACKUP_ROOT,
        help=f"Folder where the backup is saved (default: {DEFAULT_BACKUP_ROOT})",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Do not ask for confirmation before shutting down WSL",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run all checks and show what would happen, without shutting down WSL or exporting",
    )
    parser.add_argument(
        "--skip-space-check",
        action="store_true",
        help="Do not compare the distribution's used space with the free space on the backup drive",
    )
    return parser.parse_args()


def run_command(command):
    print("Running:", " ".join(str(item) for item in command))
    subprocess.run(command, check=True)


def decode_wsl_output(raw):
    """Decode bytes captured from wsl.exe.

    wsl.exe writes UTF-16 when its own output is captured, so decode the raw
    bytes ourselves instead of relying on the console code page.
    """
    if b"\x00" in raw:
        return raw.decode("utf-16-le", errors="replace")
    return raw.decode("utf-8", errors="replace")


def list_distributions():
    """Return the installed WSL distribution names, or None on failure."""
    result = subprocess.run(
        ["wsl.exe", "--list", "--quiet"],
        capture_output=True,
    )

    if result.returncode != 0:
        return None

    text = decode_wsl_output(result.stdout)
    names = [
        line.strip().lstrip("\ufeff").replace("\x00", "")
        for line in text.splitlines()
    ]
    return [name for name in names if name]


def get_used_bytes(distro):
    """Estimate the distribution's size from the used space of its root filesystem.

    Returns None if the estimate cannot be determined. This may briefly start
    the distribution.
    """
    result = subprocess.run(
        ["wsl.exe", "-d", distro, "--exec", "df", "--output=used", "-B1", "/"],
        capture_output=True,
    )

    if result.returncode != 0:
        return None

    lines = [
        line.strip()
        for line in decode_wsl_output(result.stdout).splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    try:
        return int(lines[-1])
    except ValueError:
        return None


def format_size(size_bytes):
    return f"{size_bytes / (1024 ** 3):.2f} GB"


def format_duration(seconds):
    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}"


def confirm_shutdown():
    print("WARNING: This runs 'wsl --shutdown', which stops ALL running WSL")
    print("distributions, not only the one being backed up.")
    print("Save your work in all Linux terminals and apps first.")
    print()

    try:
        answer = input("Continue? [y/N]: ")
    except EOFError:
        print()
        print("No interactive input available. Use --yes to skip this prompt.")
        return False

    return answer.strip().lower() in ("y", "yes")


def main():
    args = parse_args()
    distro = args.distro
    backup_root = args.backup_root

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = backup_root / f"{distro}-backup-{timestamp}.tar"

    print(f"WSL distribution: {distro}")
    print(f"Backup location: {backup_file}")

    if args.dry_run:
        print("Dry run: WSL will not be shut down and nothing will be exported.")

    print()

    # Confirm that wsl.exe is available (this script only works on Windows).
    if shutil.which("wsl.exe") is None:
        print("Error: wsl.exe was not found.")
        print("This script must run on Windows with WSL installed.")
        sys.exit(1)

    # Confirm that the backup drive (or share) is available.
    anchor = backup_root.anchor

    if anchor and not Path(anchor).exists():
        print(f"Error: The drive {anchor} was not found.")
        print("Connect or mount the backup drive and try again.")
        sys.exit(1)

    # Confirm that the selected WSL distribution exists (exact name match).
    installed_distributions = list_distributions()

    if installed_distributions is None:
        print("Error: Could not list WSL distributions.")
        sys.exit(1)

    installed_lower = [name.lower() for name in installed_distributions]

    if distro.lower() not in installed_lower:
        print(f"Error: WSL distribution '{distro}' was not found.")
        print()
        print("Run this command to see the installed distributions:")
        print("wsl --list --verbose")
        sys.exit(1)

    # Compare the distribution's used space with the free space on the backup drive.
    if args.skip_space_check:
        print("Skipping the free-space check.")
    else:
        existing_path = backup_root

        while not existing_path.exists():
            existing_path = existing_path.parent

        free_bytes = shutil.disk_usage(existing_path).free
        used_bytes = get_used_bytes(distro)

        if used_bytes is None:
            print("Warning: Could not estimate the distribution size.")
            print("Skipping the free-space check.")
        else:
            print(f"Estimated backup size: about {format_size(used_bytes)}")
            print(f"Free space on the backup drive: {format_size(free_bytes)}")

            if free_bytes < used_bytes:
                print()
                print("Error: There may not be enough free space for the backup.")
                print("Free up space, choose another --backup-root,")
                print("or use --skip-space-check to continue anyway.")
                sys.exit(1)

    print()

    if args.dry_run:
        print("Dry run complete. All checks passed.")
        return

    # Ask before stopping every WSL distribution.
    if not args.yes and not confirm_shutdown():
        print("Backup cancelled.")
        sys.exit(1)

    # Create the backup folder if it does not already exist.
    backup_root.mkdir(parents=True, exist_ok=True)

    # Stop WSL before creating the backup.
    print()
    print("Stopping WSL...")
    run_command(["wsl.exe", "--shutdown"])

    print()
    print("Creating backup...")
    print("This may take several minutes.")
    print()

    start_time = time.monotonic()

    # Export the complete WSL distribution.
    try:
        run_command(
            [
                "wsl.exe",
                "--export",
                distro,
                str(backup_file),
            ]
        )
    except (subprocess.CalledProcessError, KeyboardInterrupt):
        # Do not leave a partial file behind that looks like a real backup.
        if backup_file.exists():
            try:
                backup_file.unlink()
                print("Removed the incomplete backup file.")
            except OSError:
                print(f"Warning: Could not remove the incomplete file: {backup_file}")
        raise

    elapsed = time.monotonic() - start_time

    print()

    # Verify that the backup file exists and is not empty.
    if not backup_file.exists():
        print("Error: The backup file was not created.")
        sys.exit(1)

    backup_size = backup_file.stat().st_size

    if backup_size == 0:
        print("Error: The backup file is empty.")
        sys.exit(1)

    print("Backup completed successfully.")
    print(f"Backup file: {backup_file}")
    print(f"Backup size: {format_size(backup_size)}")
    print(f"Elapsed time: {format_duration(elapsed)}")


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
