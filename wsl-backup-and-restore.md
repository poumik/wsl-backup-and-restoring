# WSL Backup and Restore Guide

This guide explains how to back up and restore a complete WSL distribution using the Python script `backup_wsl.py` from this repository.

Backups are saved to the `E:\WSL-Backups` folder on the USB-SSD by default.

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

This stops all running WSL distributions before creating the backup. The script asks for confirmation first (answer `y`), unless you run it with `--yes`.

Save your work before running the script, as it will close:

- Linux terminals
- Editors and tools running inside WSL
- Desktop sessions running inside WSL
- Linux applications
- Background Linux services

## 1. Find Your WSL Distribution Name

The script needs the exact name of the distribution you want to back up. The script's default is `Ubuntu-24.04`, which is the most likely name on a current setup. Yours may be different, so check it first.

### See which distributions are installed

Open **PowerShell** and run:

```powershell
wsl --list --verbose
```

Example output:

```text
  NAME            STATE           VERSION
* Ubuntu-24.04    Running         2
  archlinux       Stopped         2
```

- `NAME` is the value you pass to `--distro`. Copy the name exactly.
- `STATE` shows whether the distribution is `Running` or `Stopped`.
- `VERSION` is the WSL version (1 or 2).
- The `*` marks the default distribution, the one `wsl` starts when you give no name. It is not part of the name.

### See which distribution you are in right now

Inside a Linux terminal, run:

```bash
echo $WSL_DISTRO_NAME
```

This prints the name of the distribution you are currently using. To see your Linux user name, run:

```bash
whoami
```

### See the WSL default distribution and version

```powershell
wsl --status
```

This shows the default distribution and the default WSL version.

### See which distributions are available to install

```powershell
wsl --list --online
```

Example (the list is longer and changes over time):

```text
NAME               FRIENDLY NAME
Debian             Debian GNU/Linux
Ubuntu-24.04       Ubuntu 24.04 LTS
archlinux          Arch Linux
kali-linux         Kali Linux Rolling
FedoraLinux-44     Fedora Linux 44
OracleLinux_9_5    Oracle Linux 9.5
```

This is only what you *can* install. The script can only back up distributions that appear in `wsl --list --verbose`.

### Use a different distribution

If your distribution is not `Ubuntu-24.04`, pass its name with `--distro` when you run the script (step 4). The script works the same way for every distribution:

```powershell
# Default: Ubuntu-24.04, saved to E:\WSL-Backups
python .\backup_wsl.py

# Other distributions
python .\backup_wsl.py --distro Ubuntu-22.04
python .\backup_wsl.py --distro Debian
python .\backup_wsl.py --distro archlinux
python .\backup_wsl.py --distro kali-linux
python .\backup_wsl.py --distro FedoraLinux-44
python .\backup_wsl.py --distro OracleLinux_9_5

# Other distribution and other backup folder
python .\backup_wsl.py --distro archlinux --backup-root D:\WSL-Backups

# Names with spaces need quotes
python .\backup_wsl.py --distro "My Distro"
```

The name must match exactly (case-insensitive). `Ubuntu` is not the same as `Ubuntu-24.04`.

If you always back up the same non-default distribution, you can change the default near the top of `backup_wsl.py` instead:

```python
DEFAULT_DISTRO = "archlinux"
```

Examples in this guide use `Ubuntu-24.04`. If your name is different, replace it in the commands below, including in the backup file names (`<name>-backup-<timestamp>.tar`).

## 2. Check That the USB-SSD Is Available

Verify the USB-SSD is mounted as drive `E:`:

```powershell
Test-Path "E:\"
```

The result should be:

```text
True
```

If you want to save backups to a different drive or folder, pass `--backup-root` when you run the script (step 4).

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

Avoid filenames like:

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

Useful options:

```powershell
# Preview: run all checks without shutting down WSL or exporting
python .\backup_wsl.py --dry-run

# Different distribution and backup folder
python .\backup_wsl.py --distro archlinux --backup-root D:\WSL-Backups
```

Run `python .\backup_wsl.py --help` for the full list. The defaults are the `Ubuntu-24.04` distribution and `E:\WSL-Backups`.

The script automatically:

1. Check that `wsl.exe` exists and that the backup drive is available.
2. Check that the WSL distribution exists.
3. Estimate the backup size and compare it with the free space on the backup drive.
4. Ask you to confirm shutting down WSL (skipped with `--yes`).
5. Create the backup folder (default `E:\WSL-Backups`) if necessary.
6. Shut down WSL.
7. Export the complete distribution to a timestamped backup.
8. Verify that the backup file is not empty and show its size and the elapsed time.

If the export fails or is cancelled, the script deletes the incomplete file.

The backup filename will resemble:

```text
E:\WSL-Backups\Ubuntu-24.04-backup-2026-09-18_14-30-00.tar
```

## 5. Verify the Backup

Check that the backup exists:

```powershell
Get-ChildItem "E:\WSL-Backups"
```

Check the backup size:

```powershell
Get-Item "E:\WSL-Backups\Ubuntu-24.04-backup-*.tar"
```

You can inspect the archive contents:

```powershell
tar -tf "E:\WSL-Backups\Ubuntu-24.04-backup-2026-09-18_14-30-00.tar" | Select-Object -First 20
```

Replace the filename with the actual backup filename.

A backup is only reliable after successful import. See step 7.

## 6. Start WSL Again

After the backup is complete, start WSL normally:

```powershell
wsl
```

Or start the distribution directly:

```powershell
wsl --distribution Ubuntu-24.04
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
  "E:\WSL-Backups\Ubuntu-24.04-backup-2026-09-18_14-30-00.tar" `
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
  Ubuntu-24.04      Stopped         2
```

### Clean up the test distribution

Once you have confirmed the backup works, remove the test copy so it does not keep using disk space.

Warning: This permanently deletes the `Ubuntu-Restored` distribution and all its contents. Double-check the name first. It does not affect `Ubuntu`.

```powershell
wsl --unregister Ubuntu-Restored
Remove-Item -Recurse -Force "$HOME\wsl-restored"
```

## 8. Restore the Original Distribution

Only use this section if you want to replace the current WSL distribution with the backup.

First, verify that the backup file exists:

```powershell
Test-Path "E:\WSL-Backups\Ubuntu-24.04-backup-2026-09-18_14-30-00.tar"
```

The result must be:

```text
True
```

Do not proceed if the result is `False`. Also make sure you have already tested this backup as described in step 7.

Shut down WSL:

```powershell
wsl --shutdown
```

Warning: The following command permanently deletes the current Ubuntu-24.04 distribution and all files inside it:

```powershell
wsl --unregister Ubuntu-24.04
```

Import the backup:

```powershell
New-Item -ItemType Directory -Force "$HOME\wsl-restored-ubuntu"

wsl --import Ubuntu-24.04 `
  "$HOME\wsl-restored-ubuntu" `
  "E:\WSL-Backups\Ubuntu-24.04-backup-2026-09-18_14-30-00.tar" `
  --version 2
```

Start the restored distribution:

```powershell
wsl --distribution Ubuntu-24.04
```

## 9. Set Your Normal Linux User After Import

Imported WSL distributions may default to the `root` user.

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

Add this configuration:

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

Save the file by:

- Press `Ctrl+O`
- Press `Enter`
- Press `Ctrl+X`

Exit the distribution:

```bash
exit
```

Restart WSL from PowerShell:

```powershell
wsl --terminate Ubuntu-24.04
wsl --distribution Ubuntu-24.04
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

Each run creates a new timestamped backup on the USB-SSD. Delete old backups to free up space, as each is a full copy of the distribution.

## Troubleshooting

### Error: WSL distribution 'Ubuntu-24.04' was not found

The script matches the distribution name exactly (upper/lower case does not matter). `Ubuntu` does not match `Ubuntu-24.04`, and the reverse. This is the most common cause.

1. List your distributions:

   ```powershell
   wsl --list --verbose
   ```

2. Copy the name from the `NAME` column. Ignore the `*` that marks the default distribution.
3. Run the script with that exact name:

   ```powershell
   python .\backup_wsl.py --distro Ubuntu
   ```

   (Here the list showed `Ubuntu`, so that is the name to use.)

For names with spaces, use quotes: `--distro "My Distro"`.

If the name in the list is exactly the one you passed and the script still cannot find it, run this and keep the output:

```powershell
python -c "import subprocess; r=subprocess.run(['wsl.exe','--list','--quiet'],capture_output=True); print(r.returncode, r.stdout)"
```

This output helps diagnose decoding issues by showing the raw bytes received from `wsl.exe`.

### Error: The drive E: was not found

Connect or mount the backup drive, or save the backup somewhere else with `--backup-root`:

```powershell
python .\backup_wsl.py --backup-root D:\WSL-Backups
```

### Error: There may not be enough free space for the backup

The script compares the space used inside the distribution with the free space on the backup drive. Free up space, choose another `--backup-root`, or use `--skip-space-check` if you know the backup will fit. The check is an estimate, so it can be wrong in either direction.

### Error: wsl.exe was not found

The script only works on Windows with WSL installed. Run it from PowerShell on Windows, not from inside Linux.

### Backup was cancelled at the confirmation prompt

The script asks before shutting down WSL. Answer `y` to continue, or run it with `--yes` to skip the prompt.

## Important Safety Notes

- Save your work before running the Python script.
- The script shuts down all running WSL distributions automatically.
- Keep the USB-SSD connected while the backup is running.
- Do not disconnect the USB-SSD during the export.
- Keep at least one backup on another drive if possible.
- Test a backup with a separate import before relying on it.
- Verify the backup before running `wsl --unregister`.
- `wsl --unregister` permanently deletes the selected WSL distribution.
- The backup file can be large because it includes the entire Linux filesystem.
- Create a new backup after major changes or installations.
