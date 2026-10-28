# Restore the project snapshot

The private dataset is `sanjuhs/route-voice-hardware-backup`. The refreshed snapshot lives under `2026-09-07-complete-snapshot/`. Earlier backup directories remain available.

1. Download `source.bundle`, `artifacts.tar.gz`, `artifact-inventory.json` and `manifest.json` using authenticated Hugging Face access.
2. Verify byte counts and SHA-256 values against `manifest.json` before extraction. Run `git bundle verify source.bundle` from a Git repository.
3. Clone the bundle into a **new empty restore directory** with `git clone source.bundle restored-project`. This bundle contains the complete history of `main` through the manifest's source commit.
4. Extract `artifacts.tar.gz` inside that new checkout. Archive names are relative to the repository root. `artifact-inventory.json` records each included path and size.
5. Reinstall the local Python and native Nix tool environments using the project scripts and tracked locks. Reinstall the prepared GF180 PDK using the pinned revision. Credentials, environment secrets, installed tool environments and caches are deliberately outside the archive.
6. Run `make -C routing-voice-chip-design test`, reproduce the reference transcription, and inspect the saved physical reports. Restoring a GDS result does not make its unresolved electrical violations disappear.

The newest GitHub commit can include the backup receipt or later source edits beyond the bundle's source commit. Any follow-up Git bundle published alongside the snapshot is incremental: fetch it into the restored repository after restoring the base bundle. Preserve snapshot revisions when reproducing measurements.

This is a project-data snapshot, not a bootable image or a backup of the entire Mac. Active work after the recorded snapshot remains outside that snapshot.
