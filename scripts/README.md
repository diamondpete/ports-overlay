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
place. A restore prunes exactly and needs no such caveat.

Consequently the fallback cannot bootstrap a new port, and refuses to run when
the old and new tags match. Build before trusting its output.

### Pruning

Because the fallback only ever adds, the list drifts upward: at jackett
0.24.2451 it held 309 packages, 72 of them surplus versions of an id it also
listed at another version, several ids carrying three or four.

`--prune` rebuilds the set instead of extending it, and changes the walk in two
ways.

**It walks only `DOTNET_TFM`**, the framework named in the port's `do-build`
publish line. Every project in the jackett graph multi-targets — `Jackett.Server`
is `net9.0;net471`, `Jackett.Common` and `DateTimeRoutines` are
`netstandard2.0;net9.0` — and an unconstrained restore pulls all of it: the
ASP.NET Core 2.3.x stack, the `NETStandard.Library` 1.6.1 galaxy of `System.*`
4.3.0 packages and their `runtime.*` satellites, and a 21 MB
`Microsoft.NETFramework.ReferenceAssemblies.net471` pack, none of which the
`net9.0` publish opens.

**It keeps one version per id**, which turns out to matter far less than the
scoping does: at jackett it drops three packages where the scoping drops 256.
`walk()` is right that NuGet fetches versions it goes on to eclipse, so most of
the surplus in the old list was duplication *across* frameworks rather than
within one, and the scoping alone accounts for it.

A restore that cannot find an eclipsed version resolves upward and says so:

```
warning NU1603: Microsoft.Extensions.Options 8.0.2 depends on
Microsoft.Extensions.Primitives (>= 8.0.0) but Microsoft.Extensions.Primitives
8.0.0 was not found. Microsoft.Extensions.Primitives 9.0.19 was resolved instead.
```

That is harmless on its own — 9.0.19 is the winner whether or not 8.0.0 is
present, so the published assemblies do not move — but the keep list below
silences it.

Together they took jackett from 309 packages and 122 MB of `${DISTDIR}/nuget` to
51 and 33 MB.

For that to hold, the port has to build one framework and mean it, which takes
more than constraining the restore in `do-build`. `dotnet publish -f` bounds the
build but not the restore publish runs for itself: that second restore re-reads
the projects, sees every framework again, and stops with `NU1101` on everything
the prune dropped, however tightly the first restore was scoped. So `post-patch`
cuts the other frameworks out of the projects instead, where no restore can put
them back:

```make
DOTNET_TFM=	net9.0

post-patch:
	${REINPLACE_CMD} "s|<TargetFrameworks>.*</TargetFrameworks>|<TargetFrameworks>${DOTNET_TFM}</TargetFrameworks>|" \
		${WRKSRC}/src/Jackett.Server/Jackett.Server.csproj \
		${WRKSRC}/src/Jackett.Common/Jackett.Common.csproj \
		${WRKSRC}/src/DateTimeRoutines/DateTimeRoutines.csproj
```

The framework-gated `ItemGroup`s upstream keeps for the frameworks that are now
gone simply stop matching, so nothing else in the projects needs touching.

The script reads `DOTNET_TFM` straight out of the Makefile rather than from
`dotnet-ports.json`, so the walk, the patch and the publish cannot disagree about
which framework the port builds. A port that does not set it cannot be pruned.

### The keep list

Some packages a restore wants cannot be derived, so `dotnet-ports.json` names
them and `--prune` hands them back:

```json
"keep": ["Microsoft.Extensions.Primitives:8.0.0"]
```

jackett needs that one entry: `Microsoft.Extensions.Options 8.0.2` resolves
`Primitives (>= 8.0.0)` to the 8.0.0 nupkg, reads it, and only then discards it
for 9.0.19 — so the file has to be there even though nothing ships out of it.
That is the `NU1603` above, and the list is how a build's findings get recorded
so the next prune does not undo them.

A pinned version is a version that can go stale, so each run checks whether
anything in the pruned set still resolves to it and reports the ones nothing
asks for any more:

```
  note: nothing left in the set resolves to these, so the keep list
  in dotnet-ports.json has outlived them and can probably lose them:
    ? Microsoft.Extensions.Primitives:8.0.0
```

Removals are the one thing the walk cannot get right on its own, so treat the
output as a hypothesis and build the port. To make a failure easier to place,
the report splits what it dropped:

```
  nuget removed, eclipsed by a version that stays (22):
  nuget removed, off the framework the port builds (236):
```

A restore that stops with `NU1101` names the package to put back, and `keep` is
where it goes. `--prune` needs no old tag to diff against, so it runs against the
current `DISTVERSION` as an audit, and it refuses to run with `--packages-dir`,
which is already exact.

### Per-port configuration

`dotnet-ports.json` maps a port directory to its restore project and to the
upstream source trees that feed `pkg-plist`:

```json
"net-p2p/jackett": {
    "restore_project": "src/Jackett.Server/Jackett.Server.csproj",
    "keep": ["Microsoft.Extensions.Primitives:8.0.0"],
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
the package, for instance. `keep` is optional and only `--prune` reads it.

### What it deliberately does not touch

`pkg-plist` lines that are *build output* rather than upstream sources — the
assemblies and native libraries directly under `%%DATADIR%%` — are left alone.
They come from the publish step and from the FreeBSD dotnet runtime pack, so
only a build can tell you when they change. The script warns whenever the
package set moved, since that is when those lines are most likely stale.

`Makefile.nuget` is written in plain byte order, matching the `:O` modifier
`shells/powershell/nuget.mk` applies. The first run normalises a few lines that
had drifted from that order.
