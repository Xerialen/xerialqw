# xerialqw — install / restore on Windows

Personal QuakeWorld install (DXerialen). Cloned on top of an nQuake base install.

## Fresh-install procedure

1. **Install nQuake to `C:\Quake\`** (the standard installer location). This delivers `id1\pak0.pak` / `pak1.pak` (copyrighted, not in this repo), `ezquake.exe`, and the baseline `qw\` directory tree.
2. **Replace `C:\Quake\` with a clone of this repo:**
   ```powershell
   # back up the nQuake install first
   Rename-Item C:\Quake C:\Quake.nquake-base
   git clone https://github.com/Xerialen/xerialqw.git C:\Quake
   # restore the copyrighted PAKs from the base install
   Copy-Item C:\Quake.nquake-base\id1\pak0.pak C:\Quake\id1\
   Copy-Item C:\Quake.nquake-base\id1\pak1.pak C:\Quake\id1\
   ```
3. Launch `C:\Quake\ezquake.exe`.

## Notes

### Font lives in two places

The QW font ships from nQuake at `qw\qwfont3.otf`, but ezquake also needs it at `ezquake\fonts\qw-font3.otf` (note the hyphen — that exact path/name is what ezquake looks for). Both copies are tracked in this repo so a fresh clone gets both. If you ever wipe `ezquake\fonts\` make sure to restore it.

### What's tracked vs. ignored

See `.gitignore`. Not tracked:

- `id1\pak0.pak` / `pak1.pak` — copyrighted Quake data, restore from a base install.
- `*.bsp` / `*.lit` — large compiled maps, fetched as needed.
- `*.pk3` — upstream redistributable game packs (huge, re-fetched by nQuake installer).
- `qw\matchinfo\screenshots\` / `qw\matchinfo\demos\temp\` — auto-generated post-match shots and temp demos.
- `ezquake\.ezquake_history`, `ezquake\sb\cache\`, `*.log` — runtime state.

### Loc files

`qw\locs\*.loc` — full set of location files for duel/4on4 maps (aerowalk, dm2/3/4/6, e1m2, schloss, etc.). Tracked so `loadloc` works out of the box.

### Config

`ezquake\configs\config.cfg` is the personal live config. Edit in-game; `cfg_save` writes back here, then `git commit` to persist.
