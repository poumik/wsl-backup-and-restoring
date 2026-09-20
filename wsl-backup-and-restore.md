# WSL Backup and Restore Guide

This guide explains how to back up and restore a complete WSL distribution using the Python script `backup_wsl.py` from this repository.

The backup is saved directly to the `E:\WSL-Backups` folder on the USB-SSD.

## What the Backup Includes

The backup is a full export of the distribution, including:

- Linux files (all users' home directories)
- Installed packages and tools (for example, a desktop environment or CLI tools you installed)
- Users
- Configuration files
- WSL settings stored inside the distribution (such as `/etc/wsl.conf`)

## Important Information

The Python script automatically runs:

```powershell
wsl.exe --shutdown
```

This stops all running WSL distributions before creating the backup.

Save your work before running the script because it will close:

- Linux terminals
- Editors and tools running inside WSL
- Desktop sessions running inside WSL
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

The name must match exactly. If you change it, also replace `Ubuntu` in the example commands below.

## 2. Check That the USB-SSD Is Available

Confirm that the USB-SSD is mounted as drive `E:`:

```powershell
Test-Path "E:\"
```

The result should be:

```text
True
```

## 3. Get the Script

Keep the script on your Windows internal drive, not inside WSL or on the backup drive.

Create a scripts folder:

```powershell
New-Item -ItemType Directory -Force "$HOME\Documents\Scripts"
```

The folder will be:

```text
C:\Users\YourWindowsUsername\Documents\Scripts
```

Then put `backup_wsl.py` from this repository into that folder, using either method:

- **Clone the repository** (requires Git) and copy `backup_wsl.py` into the folder, or run the script directly from the cloned repository.
- **Download the file** from the repository page (the **Raw** view, then **Save as**) and save it as `backup_wsl.py`.

Make sure the filename is exactly:

```text
backup_wsl.py
```

It must not end up as:

```text
backup_wsl.py.txt
```

Check with:

```powershell
Get-ChildItem "$HOME\Documents\Scripts"
```

Using the file from the repository (instead of copy-pasting it) keeps you on the latest version of the script.

## 4. Run the Backup Script

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

If the export fails or is cancelled, the script deletes the incomplete file.

The backup will look similar to:

```text
E:\WSL-Backups\Ubuntu-backup-2026-09-18_14-30-00.tar
```

## 5. Verify the Backup

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

A backup is only proven good once you have imported it successfully. See step 7.

## 6. Start WSL Again

After the backup is complete, start WSL normally:

```powershell
wsl
```

Or start Ubuntu directly:

```powershell
wsl --distribution Ubuntu
```

## 7. Test the Backup Without Deleting the Original

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

Check the tools you rely on. For example:

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

### Clean up the test distribution

Once you have confirmed the backup works, remove the test copy so it does not keep using disk space.

Warning: this permanently deletes the `Ubuntu-Restored` distribution and everything inside it. Double-check the name first. It does not affect `Ubuntu`.

```powershell
wsl --unregister Ubuntu-Restored
Remove-Item -Recurse -Force "$HOME\wsl-restored"
```

## 8. Restore the Original Distribution

Only use this section if you want to replace the current WSL distribution with the backup.

First, verify that the backup file exists:

```powershell
Test-Path "E:\WSL-Backups\Ubuntu-backup-2026-09-18_14-30-00.tar"
```

The result must be:

```text
True
```

Do not continue if the result is `False`. Also make sure you have already tested this backup as described in step 7.

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

## 9. Set Your Normal Linux User After Import

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

If the file already has a `[user]` section, edit it instead of adding a second one.

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

## 10. Create Future Backups

Whenever you want to create another backup, open PowerShell and run:

```powershell
Set-Location "$HOME\Documents\Scripts"
python .\backup_wsl.py
```

If necessary, use:

```powershell
py .\backup_wsl.py
```

Each run creates a new timestamped backup on the USB-SSD. Delete old backups you no longer need, since each one is a full copy of the distribution.

## Important Safety Notes

- Save your work before running the Python script.
- The script shuts down all running WSL distributions automatically.
- Keep the USB-SSD connected while the backup is running.
- Do not disconnect the USB-SSD during the export.
- Keep at least one backup on another drive if possible.
- Test a backup with a separate import before relying on it.
- Do not run `wsl --unregister` until you have verified the backup.
- `wsl --unregister` permanently deletes the selected WSL distribution.
- The backup file can be large because it includes the entire Linux filesystem.
- Create a new backup after major changes or installations.
