# WSL Backup and Restore

A Python script that backs up a Windows Subsystem for Linux (WSL) distribution, plus a guide for restoring it manually with `wsl --import`.

## Quick start

```powershell
# From the repo root:
python .\backup_wsl.py
# or: py .\backup_wsl.py
```

Common variations:

```powershell
# Different distribution and backup folder
python .\backup_wsl.py --distro Ubuntu-24.04 --backup-root D:\WSL-Backups

# Run all checks without shutting down WSL or exporting anything
python .\backup_wsl.py --dry-run
```

## Options

| Option | Description |
| --- | --- |
| `--distro NAME` | WSL distribution to back up, exactly as shown by `wsl --list --verbose` (default: `Ubuntu`) |
| `--backup-root PATH` | Folder where the backup is saved (default: `E:\WSL-Backups`) |
| `-y`, `--yes` | Skip the confirmation prompt before shutting down WSL (for automation) |
| `--dry-run` | Run all checks and show what would happen; does not shut down WSL, create folders, or export |
| `--skip-space-check` | Skip the free-space check |

Run `python .\backup_wsl.py --help` to see the same list.

## What it does

- Backs up the WSL distribution via `wsl --export`
- Saves to `<backup-root>\<distro>-backup-<timestamp>.tar` (default: `E:\WSL-Backups\Ubuntu-backup-<timestamp>.tar`)
- Checks that `wsl.exe` exists, that the backup drive is available, and that the distribution is installed (exact name match)
- Compares the distribution's used space with the free space on the backup drive (an estimate; see below)
- **Asks for confirmation, then shuts down all WSL distributions** before exporting (closes terminals, editors, desktop sessions, etc.)
- Verifies the backup file exists and is not empty, and prints its size and the elapsed time
- Removes the partial `.tar` file if the export fails or is cancelled

## Key conventions

- The defaults are the `DEFAULT_DISTRO` and `DEFAULT_BACKUP_ROOT` values at the top of `backup_wsl.py`. Use the command-line options for one-off changes, or edit the defaults if you always use the same setup.
- Run `wsl --list --verbose` to see installed distributions.
- The distribution name must match exactly (for example, `Ubuntu` does not match `Ubuntu-24.04`).
- The backup folder is created automatically if missing.

## Safe operations

Read this before using the script:

- **The backup can be huge.** It is the entire Linux filesystem of the distribution, and every run creates a new full copy. Delete old backups you no longer need.
- **All WSL distributions are shut down**, not just the one being backed up. The script asks for confirmation first; save your work in all Linux terminals and apps before answering `y`. `--yes` skips the prompt.
- **The free-space check is an estimate.** It compares the used space inside the distribution with the free space on the backup drive. The real `.tar` size can differ. Use `--skip-space-check` if you know it will fit.
- **There are no automatic retries.** If a backup fails, the incomplete file is removed and you need to run the script again.
- **Keep the backup drive connected** for the whole export.
- **Test a backup before relying on it.** Import it as a separate distribution first (see the guide), and never run `wsl --unregister` on the original until you have verified the backup.

## Common gotchas

- The script **fails** if the backup drive is not accessible. Connect or mount it first (for example, the USB-SSD for `E:\`).
- The script only works on Windows (it needs `wsl.exe`).
- `--dry-run` may briefly start the distribution to estimate its size, but it does not shut anything down or write a backup.

## One-time vs repeatable backups

Microsoft's command is the essential backup operation:

```powershell
wsl --export Ubuntu "E:\WSL-Backups\Ubuntu-backup.tar"
```

The Python script automates that command by:

- Checking that `wsl.exe` and the backup drive are available.
- Checking that the named distribution is installed.
- Estimating the size and comparing it with the free space.
- Asking for confirmation, then running `wsl --shutdown`.
- Adding the current date and time to the filename and creating the backup folder.
- Running `wsl --export`.
- Checking that the backup file was created and is not empty.

If you only need a one-time backup, use Microsoft's direct command. The Python version is useful when you want repeatable, timestamped backups with one command.

## Restoring

The script only creates backups. Restoring is manual: see [`wsl-backup-and-restore.md`](./wsl-backup-and-restore.md) for the full restore flow (uses `wsl --import`), including how to test a backup safely before replacing anything.

## Usage

1. Make sure the backup drive is connected.
2. Run the backup script (optionally with `--dry-run` first).
3. To restore, follow the steps in `wsl-backup-and-restore.md`.

## Disclaimer

**Use at your own risk.** The repository maintainer is not responsible for any data loss, corruption, or damage resulting from the use or misuse of this script or accompanying guides. WSL backup/restore involves the entire Linux filesystem and can be large; ensure you have adequate storage and have verified backups before performing `wsl --unregister` or restoring. Always save your work before running the script, as it shuts down all WSL distributions. Keep separate copies of important data whenever possible.
