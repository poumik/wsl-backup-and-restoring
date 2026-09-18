# WSL Backup and Restore Guide

This guide explains how to back up and restore a complete WSL distribution using a Python script.

The backup is saved directly to the `E:\WSL-Backups` folder on the USB-SSD.

## What the Backup Includes

The backup includes:

- Linux files
- Installed packages
- Users
- Configuration files
- OpenCode installation
- XFCE desktop configuration
- WSL settings stored inside the distribution

## Important Information

The Python script automatically runs:

```powershell
wsl.exe --shutdown
```

This stops all running WSL distributions before creating the backup.

Save your work before running the script because it will close:

- Ubuntu terminals
- OpenCode
- XFCE desktop sessions
- Linux applications
- Background Linux services

## 1. Check the WSL Distribution Name

Open **PowerShell** and run:

```powershell
wsl --list --verbose
```

Example output:

```text
  NAME      STATE           VERSION
* Ubuntu    Running         2
```

This guide uses `Ubuntu` as the distribution name.

If your distribution has a different name, change this line in the Python script:

```python
DISTRO_NAME = "Ubuntu"
```

For example:

```python
DISTRO_NAME = "Ubuntu-24.04"
```

## 2. Check That the USB-SSD Is Available

Confirm that the USB-SSD is mounted as drive `E:`:

```powershell
Test-Path "E:\"
```

The result should be:

```text
True
```

## 3. Create a Scripts Folder

Save the Python script on your Windows internal drive, not inside WSL or on the backup drive.

Run:

```powershell
New-Item -ItemType Directory -Force "$HOME\Documents\Scripts"
```

The folder will be:

```text
C:\Users\YourWindowsUsername\Documents\Scripts
```

## 4. Save the Python Backup Script

Open Notepad:

```powershell
notepad "$HOME\Documents\Scripts\backup_wsl.py"
```

Paste the following code into Notepad:

```python
from pathlib import Path
from datetime import datetime
import subprocess
import sys


# Change this if your WSL distribution has a different name.
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
    # This closes running WSL terminals, OpenCode, XFCE, and Linux processes.
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
```

Save the file as:

```text
backup_wsl.py
```

In Notepad, choose:

```text
File → Save
```

Make sure the filename is exactly:

```text
backup_wsl.py
```

It must not be saved as:

```text
backup_wsl.py.txt
```

## 5. Run the Backup Script

Open PowerShell and move to the script folder:

```powershell
Set-Location "$HOME\Documents\Scripts"
```

Run the script:

```powershell
python .\backup_wsl.py
```

If `python` is not recognized, try:

```powershell
py .\backup_wsl.py
```

The script will automatically:

1. Check that drive `E:` exists.
2. Create `E:\WSL-Backups` if necessary.
3. Check that the WSL distribution exists.
4. Shut down WSL.
5. Export the complete distribution.
6. Create a timestamped backup.
7. Verify that the backup file is not empty.

The backup will look similar to:

```text
E:\WSL-Backups\Ubuntu-backup-2026-09-18_14-30-00.tar
```

## 6. Verify the Backup

Check that the backup exists:

```powershell
Get-ChildItem "E:\WSL-Backups"
```

Check the backup size:

```powershell
Get-Item "E:\WSL-Backups\Ubuntu-backup-*.tar"
```

You can inspect the archive contents:

```powershell
tar -tf "E:\WSL-Backups\Ubuntu-backup-2026-09-18_14-30-00.tar" | Select-Object -First 20
```

Replace the filename with the actual backup filename.

## 7. Start WSL Again

After the backup is complete, start WSL normally:

```powershell
wsl
```

Or start Ubuntu directly:

```powershell
wsl --distribution Ubuntu
```

## 8. Test the Backup Without Deleting the Original

It is recommended to test the backup by importing it as a separate WSL distribution.

Create a restore folder:

```powershell
New-Item -ItemType Directory -Force "$HOME\wsl-restored"
```

Import the backup:

```powershell
wsl --import Ubuntu-Restored `
  "$HOME\wsl-restored" `
  "E:\WSL-Backups\Ubuntu-backup-2026-09-18_14-30-00.tar" `
  --version 2
```

Replace the filename with your actual backup filename.

Start the restored distribution:

```powershell
wsl --distribution Ubuntu-Restored
```

Check your files:

```bash
ls -la
```

Check OpenCode:

```bash
which opencode
opencode --version
```

Check your current Linux user:

```bash
whoami
```

Exit the restored distribution:

```bash
exit
```

List the installed WSL distributions:

```powershell
wsl --list --verbose
```

You should see something similar to:

```text
  NAME              STATE           VERSION
* Ubuntu-Restored   Stopped         2
  Ubuntu            Stopped         2
```

## 9. Restore the Original Distribution

Only use this section if you want to replace the current WSL distribution with the backup.

First, verify that the backup file exists:

```powershell
Test-Path "E:\WSL-Backups\Ubuntu-backup-2026-09-18_14-30-00.tar"
```

The result must be:

```text
True
```

Do not continue if the result is `False`.

Shut down WSL:

```powershell
wsl --shutdown
```

Warning: The following command permanently deletes the current Ubuntu distribution and all files inside it:

```powershell
wsl --unregister Ubuntu
```

Import the backup:

```powershell
New-Item -ItemType Directory -Force "$HOME\wsl-restored-ubuntu"

wsl --import Ubuntu `
  "$HOME\wsl-restored-ubuntu" `
  "E:\WSL-Backups\Ubuntu-backup-2026-09-18_14-30-00.tar" `
  --version 2
```

Start the restored distribution:

```powershell
wsl --distribution Ubuntu
```

## 10. Set Your Normal Linux User After Import

Imported WSL distributions may start as the `root` user.

Check the current user:

```bash
whoami
```

Find your normal Linux username:

```bash
ls /home
```

Edit the WSL configuration:

```bash
sudo nano /etc/wsl.conf
```

Add the following configuration:

```ini
[user]
default=YOUR_LINUX_USERNAME
```

Replace `YOUR_LINUX_USERNAME` with the username shown in `/home`.

For example:

```ini
[user]
default=alex
```

Save the file:

- Press `Ctrl+O`
- Press `Enter`
- Press `Ctrl+X`

Exit Ubuntu:

```bash
exit
```

Restart WSL from PowerShell:

```powershell
wsl --terminate Ubuntu
wsl --distribution Ubuntu
```

Check the current user:

```bash
whoami
```

It should now show your normal Linux username.

## 11. Create Future Backups

Whenever you want to create another backup, open PowerShell and run:

```powershell
Set-Location "$HOME\Documents\Scripts"
python .\backup_wsl.py
```

If necessary, use:

```powershell
py .\backup_wsl.py
```

Each run creates a new timestamped backup on the USB-SSD.

## Important Safety Notes

- Save your work before running the Python script.
- The script shuts down all running WSL distributions automatically.
- Keep the USB-SSD connected while the backup is running.
- Do not disconnect the USB-SSD during the export.
- Keep at least one backup on another drive if possible.
- Do not run `wsl --unregister` until you have verified the backup.
- `wsl --unregister` permanently deletes the selected WSL distribution.
- The backup file can be large because it includes the entire Linux filesystem.
- Create a new backup after major changes or installations.
````_
