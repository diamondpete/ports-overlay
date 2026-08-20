# Scripts

## update-dotnet-port.py

Updates a dotnet port to a new upstream tag, in place:

```sh
./scripts/update-dotnet-port.py net-p2p/jackett v0.24.2419
```

It rewrites four files and then prints what it changed, so review with
`git diff` before committing:

| File | What changes |
| --- | --- |
| `Makefile` | `DISTVERSION` |
| `pkg-plist` | entries for files upstream added or removed |
| `Makefile.nuget` | the NuGet package set the new tree restores |
| `distinfo` | checksums for every `.nupkg` plus the GitHub tarball |

Checksums already recorded in `distinfo` are reused, so only genuinely new
packages get downloaded.

### Where the package set comes from

In order of preference:

1. `--packages-dir DIR` — a NuGet global-packages folder from a restore you
   already ran (`dotnet restore <project> --packages DIR`). Its `<id>/<version>/`
   layout *is* the DISTFILES list, so this is exact.
2. A real `dotnet restore`, run automatically when a .NET SDK is on `PATH`
   (override the binary with `--dotnet`, or skip with `--no-restore`).
3. Walking `api.nuget.org` directly, when no SDK is available.

Option 3 is an approximation and is labelled `UNVERIFIED` in the output. It
cannot reproduce a restore: measured against the hand-maintained list at
jackett 0.24.2288 it emitted 357 packages where the port needed 300, keeping
every version the walk visits — including ones NuGet's conflict resolution
discards — while still missing 16 a restore genuinely needs.

Two rules keep it from doing damage.

**It never writes its own output as the answer.** It walks *both* tags and
applies the difference to the list already in `Makefile.nuget`, which a real
restore produced. Errors identical at both tags cancel out. Rebuilding the list
wholesale instead bakes every one of them into the diff.

**It only ever adds.** An unused `.nupkg` in `${DISTDIR}/nuget` costs a
download and nothing else; a missing one fails the restore outright:

```
error NU1101: Unable to find package System.IO. No packages exist with this id
```

The walk cannot distinguish a package that is truly gone from one it fails to
reach — picking a dependency group per target framework does not always follow
NuGet down to the same leaves — so removals are reported with `?` and left in
place. `--prune` applies them anyway, which is only safe if you are going to
build. A restore prunes exactly and needs no such caveat.

Consequently the fallback cannot bootstrap a new port, and refuses to run when
the old and new tags match. Build before trusting its output.

### Per-port configuration

`dotnet-ports.json` maps a port directory to its restore project and to the
upstream source trees that feed `pkg-plist`:

```json
"net-p2p/jackett": {
    "restore_project": "src/Jackett.Server/Jackett.Server.csproj",
    "plist_maps": [
        {
            "plist": "%%DATADIR%%/Definitions/",
            "source": "src/Jackett.Common/Definitions/",
            "include": ["*.yml"]
        }
    ]
}
```

`include` and `exclude` are optional lists of shell globs matched against the
file name — jackett's `Definitions/` ships a `schema.json` that never lands in
the package, for instance.

### What it deliberately does not touch

`pkg-plist` lines that are *build output* rather than upstream sources — the
assemblies and native libraries directly under `%%DATADIR%%` — are left alone.
They come from the publish step and from the FreeBSD dotnet runtime pack, so
only a build can tell you when they change. The script warns whenever the
package set moved, since that is when those lines are most likely stale.

`Makefile.nuget` is written in plain byte order, matching the `:O` modifier
`shells/powershell/nuget.mk` applies. The first run normalises a few lines that
had drifted from that order.
