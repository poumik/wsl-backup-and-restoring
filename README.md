# WSL Backup and Restore

A Python script to back up and restore Windows Subsystem for Linux (WSL) distributions.

## Quick start

```powershell
# From the repo root:
python .\backup_wsl.py
# or: py .\backup_wsl.py
```

## What it does

- Backs up the WSL distribution (default: `Ubuntu-24.04`) via `wsl --export`
- Saves to `E:\WSL-Backups\<distro>-backup-<timestamp>.tar`
- **Shuts down all WSL distributions** before exporting (closes terminals, OpenCode, etc.)
- Requires drive `E:` (USB‑SSD etc. ) to be mounted

## Key conventions

- `DISTRO_NAME = "Ubuntu"` in `backup_wsl.py:8` — change if your distro has a different name
- Run `wsl --list --verbose` to see installed distributions
- Backup folder: `E:\WSL-Backups` (created automatically if missing)

## Custom backup destination

You can change the backup drive or folder by editing the `BACKUP_FOLDER` variable in `backup_wsl.py`. The default saves to `E:\WSL-Backups`. Adjust the path as needed (e.g., `C:\Backups` or any other location). The script will create the folder if it does not exist.

## Common gotchas

- Script will **fail** if `E:\` is not accessible — connect/mount the USB‑SSD first
- Script **shuts down WSL** — save work in all Linux terminals/apps first
- Backup file size is the entire distro filesystem — may be large

## Restoring

See [`wsl-backup-and-restore.md`](./wsl-backup-and-restore.md) for the full restore flow (uses `wsl --import`).

## Usage

1. Ensure drive `E:` is mounted.
2. Run the backup script.
3. To restore, follow the steps in `wsl-backup-and-restore.md`.
