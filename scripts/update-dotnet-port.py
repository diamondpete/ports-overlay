#!/usr/bin/env python3
"""Update a dotnet port to a new upstream tag.

Rewrites, for the port named on the command line:

  Makefile        DISTVERSION
  pkg-plist       files added/removed upstream, per scripts/dotnet-ports.json
  Makefile.nuget  the NuGet package set the new tree restores
  distinfo        checksums for every .nupkg plus the GitHub tarball

The package set comes from a real `dotnet restore` when a .NET SDK is
available (or --packages-dir points at one someone already ran); otherwise it
falls back to walking api.nuget.org, which is close but unverified.

  ./scripts/update-dotnet-port.py net-p2p/jackett v0.24.2419
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nuget_walk as W  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "scripts", "dotnet-ports.json")
TREE_API = "https://api.github.com/repos/%s/%s/git/trees/%s?recursive=1"
CODELOAD = "https://codeload.github.com/%s/%s/tar.gz/%s"
NUPKG = "https://api.nuget.org/v3-flatcontainer/%s/%s/%s.%s.nupkg"


def die(msg: str):
    sys.exit("error: " + msg)


def note(msg: str):
    print(msg, file=sys.stderr)


# ---------------------------------------------------------------- sorting


def sortkey(pkg) -> str:
    """Plain byte order, which is what nuget.mk's :O modifier applies anyway."""
    return "%s:%s" % pkg if isinstance(pkg, tuple) else pkg


# ---------------------------------------------------------------- port files


class Port:
    def __init__(self, path: str):
        self.dir = os.path.join(ROOT, path)
        if not os.path.isdir(self.dir):
            die("no such port directory: %s" % path)
        self.name = path.replace("\\", "/")
        self.makefile = self.read("Makefile")
        self.vars = dict(re.findall(r"^([A-Z_][A-Z0-9_]*)[?+]?=[ \t]*(.*?)[ \t]*$",
                                    self.makefile, re.M))

    def read(self, name: str) -> str:
        with open(os.path.join(self.dir, name), encoding="utf-8", newline="") as fh:
            return fh.read()

    def write(self, name: str, text: str):
        with open(os.path.join(self.dir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)

    def var(self, key: str) -> str:
        if key not in self.vars:
            die("%s does not set %s" % (self.name, key))
        return self.vars[key]

    @property
    def account(self) -> str:
        return self.vars.get("GH_ACCOUNT", self.var("PORTNAME"))

    @property
    def project(self) -> str:
        return self.vars.get("GH_PROJECT", self.var("PORTNAME"))

    def tag(self, distversion: str) -> str:
        return self.vars.get("DISTVERSIONPREFIX", "") + distversion + self.vars.get("DISTVERSIONSUFFIX", "")

    def tarball(self, distversion: str) -> str:
        return "%s-%s-%s_GH0.tar.gz" % (self.account, self.project, self.tag(distversion))


# ---------------------------------------------------------------- github


def gh_headers() -> dict:
    hdrs = {"User-Agent": "ports-overlay-update/1",
            "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        try:
            token = subprocess.run(["gh", "auth", "token"], capture_output=True,
                                   text=True, timeout=15).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            token = ""
    if token:
        hdrs["Authorization"] = "Bearer " + token
    return hdrs


def tree_files(port: Port, tag: str) -> set:
    """Every blob path in the repo at `tag`."""
    req = urllib.request.Request(TREE_API % (port.account, port.project, tag),
                                 headers=gh_headers())
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            die("tag %s not found in %s/%s" % (tag, port.account, port.project))
        raise
    if data.get("truncated"):
        die("tree listing for %s was truncated; this script needs the full tree" % tag)
    return {e["path"] for e in data["tree"] if e["type"] == "blob"}


def extract(tarpath: str, dest: str) -> str:
    """Unpack a GitHub tarball and return the path to its single top directory."""
    os.makedirs(dest, exist_ok=True)
    with tarfile.open(tarpath) as tf:
        names = tf.getnames()
        top = names[0].split("/")[0]
        kwargs = {"filter": "data"} if sys.version_info >= (3, 12) else {}
        tf.extractall(dest, **kwargs)
    return os.path.join(dest, top)


def fetch_tarball(port: Port, tag: str, dest: str) -> tuple:
    """Download the GitHub tarball to `dest`; return (sha256, size)."""
    req = urllib.request.Request(CODELOAD % (port.account, port.project, tag),
                                 headers={"User-Agent": "ports-overlay-update/1"})
    digest, size = hashlib.sha256(), 0
    with urllib.request.urlopen(req, timeout=180) as resp, open(dest, "wb") as fh:
        declared = int(resp.headers.get("Content-Length") or 0)
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            digest.update(chunk)
            fh.write(chunk)
            size += len(chunk)
    if declared and size != declared:
        die("%s download stopped at %d of %d bytes; retry" % (tag, size, declared))
    return digest.hexdigest(), size


# ---------------------------------------------------------------- pkg-plist


def match_any(name: str, patterns) -> bool:
    import fnmatch
    return any(fnmatch.fnmatch(name, p) for p in patterns)


def plist_entries(files: set, maps: list) -> set:
    """Translate upstream source paths into the pkg-plist entries they become."""
    out = set()
    for spec in maps:
        src, dst = spec["source"], spec["plist"]
        inc, exc = spec.get("include"), spec.get("exclude")
        for path in files:
            if not path.startswith(src):
                continue
            rel = path[len(src):]
            base = rel.rsplit("/", 1)[-1]
            if inc and not match_any(base, inc):
                continue
            if exc and match_any(base, exc):
                continue
            out.add(dst + rel)
    return out


def update_plist(port: Port, old_files: set, new_files: set, maps: list) -> tuple:
    old = plist_entries(old_files, maps)
    new = plist_entries(new_files, maps)
    added, removed = new - old, old - new
    lines = [ln for ln in port.read("pkg-plist").splitlines() if ln.strip()]
    managed = {spec["plist"] for spec in maps}
    owned = {ln for ln in lines if any(ln.startswith(p) for p in managed)}
    kept = [ln for ln in lines if ln not in owned or ln in new]
    port.write("pkg-plist", "\n".join(sorted(set(kept) | new)) + "\n")
    # entries the plist listed that the tree diff did not predict, i.e. the
    # plist and the old tag had already drifted apart
    return added, removed, (owned - new) - removed


# ---------------------------------------------------------------- nuget set


def sdk_available(dotnet: str) -> bool:
    try:
        out = subprocess.run([dotnet, "--list-sdks"], capture_output=True,
                             text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return False
    return out.returncode == 0 and bool(out.stdout.strip())


def packages_from_dir(path: str) -> set:
    """A NuGet global-packages folder is <id>/<version>/ — exactly DISTFILES."""
    out = set()
    for pid in os.listdir(path):
        pdir = os.path.join(path, pid)
        if not os.path.isdir(pdir):
            continue
        for ver in os.listdir(pdir):
            if os.path.isdir(os.path.join(pdir, ver)):
                out.add((pid, ver))
    return out


def cased_ids(pkgs: set, workdir: str) -> set:
    """A restore folder lower-cases ids; recover the casing from each .nuspec."""
    fixed = set()
    for pid, ver in pkgs:
        spec = os.path.join(workdir, pid, ver, pid + ".nuspec")
        real = pid
        if os.path.exists(spec):
            try:
                root = ET.parse(spec).getroot()
                for el in root.iter():
                    if el.tag.split("}")[-1] == "id" and el.text:
                        real = el.text.strip()
                        break
            except ET.ParseError:
                pass
        fixed.add((real, ver))
    return fixed


def restore_packages(dotnet: str, srcdir: str, project: str, workdir: str) -> set:
    proj = os.path.join(srcdir, project)
    if not os.path.exists(proj):
        die("restore project not found in the new tree: %s" % project)
    note("running dotnet restore (this pulls the whole graph, give it a minute)")
    res = subprocess.run([dotnet, "restore", proj, "--packages", workdir],
                         capture_output=True, text=True)
    if res.returncode != 0:
        note(res.stdout[-4000:])
        note(res.stderr[-4000:])
        die("dotnet restore failed")
    return cased_ids(packages_from_dir(workdir), workdir)


def walk_delta(old_tree: str, new_tree: str, project: str, baseline: set) -> tuple:
    """What the walk says the bump adds, on top of the list already recorded.

    The walk cannot reproduce `dotnet restore`.  It keeps versions NuGet's
    conflict resolution discards, and — the part that matters here — it misses
    packages a restore genuinely needs, because picking a dependency group per
    target framework does not always follow NuGet down to the same leaves.
    Walking both tags cancels the errors that are identical at each, but not
    these: a package the walk cannot see at either tag looks like a removal.

    An unused .nupkg in ${DISTDIR}/nuget costs a download and nothing else, so
    additions are applied.  A missing one fails the restore outright (NU1101),
    so removals are only ever reported, unless --prune says otherwise.
    """
    note("walking the new tree")
    new = walk_packages(new_tree, project, baseline)
    note("walking the old tree, to subtract the walk's own quirks")
    old = walk_packages(old_tree, project, baseline)
    gained, lost = new - old, (old - new) & baseline

    # One removal is safe: the version a package is being bumped *from*.  The
    # walk agrees it is gone and the same id is arriving at a new version, so
    # this is a bump rather than the walk losing sight of a live package.
    bumped = {pid.lower() for pid, _ in gained}
    superseded = {(pid, ver) for pid, ver in lost if pid.lower() in bumped}
    return (baseline | gained) - superseded, lost - superseded


def walk_packages(srcdir: str, project: str, carry: set) -> set:
    """Walk api.nuget.org from the project's PackageReferences."""
    proj_path = os.path.join(srcdir, project)
    if not os.path.exists(proj_path):
        die("restore project not found under %s: %s" % (srcdir, project))
    root = ET.parse(proj_path).getroot()
    projects = [(project, root)]
    for rel in W.project_refs(root):
        p = os.path.normpath(os.path.join(os.path.dirname(proj_path), rel))
        if os.path.exists(p):
            projects.append((rel, ET.parse(p).getroot()))

    out: set = set()
    for label, proj in projects:
        tfms = W.project_tfms(proj)
        for tfm in tfms:
            roots = W.package_refs(proj, tfm)
            if proj is root:
                for _, dep in projects[1:]:
                    chain = W.compat_chain(tfm)
                    dep_tfms = W.project_tfms(dep)
                    best = min(dep_tfms, key=lambda t: chain.index(t) if t in chain else 99)
                    roots += W.package_refs(dep, best)
            if tfm == "netstandard2.0":
                roots.append(("NETStandard.Library", W.Range("2.0.3")))
            note("  walking %s/%s (%d direct refs)" % (label, tfm, len(roots)))
            out |= W.walk(roots, tfm, warn=lambda m: note("  ! " + m))

    # RID-specific satellites (runtime.unix.*, runtime.any.*) come from
    # runtime.json inside the nupkgs, which the walk never opens.  Carry over
    # the ones whose base package survived the bump.
    base = {"%s:%s" % (p, v) for p, v in out}
    rid = re.compile(r"^runtime\.[^.]+(?:\.[0-9][^.]*)?(?:-[a-z0-9]+)?\.(.+)$")
    for pid, ver in carry:
        if not pid.lower().startswith("runtime."):
            continue
        m = rid.match(pid)
        if m and "%s:%s" % (m.group(1), ver) in base:
            out.add((pid, ver))
    return out


# ---------------------------------------------------------------- writers


def parse_nupkgs(text: str) -> list:
    """The first entry shares the NUGET_NUPKGS= line, the rest are indented."""
    return [(m.group(1), m.group(2))
            for m in re.finditer(r"(?:^|[ \t])([A-Za-z][A-Za-z0-9_.-]*):([^\s\\]+)", text, re.M)]


def write_nuget_makefile(port: Port, pkgs: set, previous: list) -> list:
    """Keep the order already in the file, slotting new entries into place.

    nuget.mk sorts with :O regardless, so order is cosmetic — but rewriting it
    wholesale buries a three-package bump in a hundred lines of churn.
    """
    ordered = [p for p in previous if p in pkgs]
    for pkg in sorted(pkgs.difference(previous), key=sortkey):
        at = len(ordered)
        for i, seen in enumerate(ordered):
            if sortkey(seen) > sortkey(pkg):
                at = i
                break
        ordered.insert(at, pkg)
    body = " \\\n".join("\t\t%s:%s" % p for p in ordered).lstrip("\t")
    port.write("Makefile.nuget", "NUGET_GROUPS=\tNUGET\nNUGET_NUPKGS=\t%s\n" % body)
    return ordered


def distinfo_name(pid: str, ver: str) -> str:
    return "nuget/%s.%s.nupkg" % (pid.lower(), ver.lower())


def fetch_nupkg(pid: str, ver: str) -> tuple:
    lid, lv = pid.lower(), ver.lower()
    req = urllib.request.Request(NUPKG % (lid, lv, lid, lv),
                                 headers={"User-Agent": "ports-overlay-update/1"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                blob = resp.read()
            return hashlib.sha256(blob).hexdigest(), len(blob)
        except (urllib.error.HTTPError, OSError) as exc:
            if isinstance(exc, urllib.error.HTTPError) and exc.code == 404:
                die("nuget.org has no %s %s" % (pid, ver))
            if attempt == 2:
                raise
    raise RuntimeError("unreachable")


def write_distinfo(port: Port, pkgs, tarball: str, tar_sha: str, tar_size: int):
    """Reuse checksums already recorded; only fetch packages that are new.

    DISTFILES comes from NUGET_NUPKGS:O, so sort by "id:version" in byte order
    rather than following the order Makefile.nuget happens to list, which is
    kept cosmetically stable and drifts out of :O order as entries are added.
    """
    old = port.read("distinfo")
    known = {}
    for m in re.finditer(r"^SHA256 \((.+?)\) = ([0-9a-f]+)$", old, re.M):
        known[m.group(1)] = [m.group(2), None]
    for m in re.finditer(r"^SIZE \((.+?)\) = (\d+)$", old, re.M):
        if m.group(1) in known:
            known[m.group(1)][1] = int(m.group(2))

    wanted = [(pid, ver, distinfo_name(pid, ver)) for pid, ver in sorted(pkgs, key=sortkey)]
    missing = [w for w in wanted if known.get(w[2], [None, None])[1] is None]
    if missing:
        note("fetching %d new .nupkg%s for checksums" % (len(missing), "" if len(missing) == 1 else "s"))
        with ThreadPoolExecutor(8) as ex:
            futs = {ex.submit(fetch_nupkg, pid, ver): name for pid, ver, name in missing}
            for fut in futs:
                known[futs[fut]] = list(fut.result())

    lines = ["TIMESTAMP = %d" % int(time.time())]
    for _, _, name in wanted:
        sha, size = known[name]
        lines.append("SHA256 (%s) = %s" % (name, sha))
        lines.append("SIZE (%s) = %d" % (name, size))
    lines.append("SHA256 (%s) = %s" % (tarball, tar_sha))
    lines.append("SIZE (%s) = %d" % (tarball, tar_size))
    port.write("distinfo", "\n".join(lines) + "\n")


def bump_makefile(port: Port, new_version: str):
    text, hits = re.subn(r"^(DISTVERSION=[ \t]*).*$", lambda m: m.group(1) + new_version,
                         port.makefile, count=1, flags=re.M)
    if not hits:
        die("could not rewrite DISTVERSION in the Makefile")
    port.write("Makefile", text)


# ---------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("port", help="port directory, e.g. net-p2p/jackett")
    ap.add_argument("version", help="new upstream tag or version, e.g. v0.24.2419")
    ap.add_argument("--packages-dir", help="NuGet global-packages folder from a restore "
                                           "someone already ran; skips resolving entirely")
    ap.add_argument("--dotnet", default=os.environ.get("DOTNET", "dotnet"),
                    help="dotnet binary to restore with (default: dotnet)")
    ap.add_argument("--no-restore", action="store_true",
                    help="never shell out to dotnet; always walk api.nuget.org")
    ap.add_argument("--keep-src", metavar="DIR",
                    help="extract the new tree here and leave it in place")
    ap.add_argument("--prune", action="store_true",
                    help="also apply the offline walk's removals; unsafe, since a "
                         "package it cannot see looks the same as one that is gone")
    args = ap.parse_args()

    with open(CONFIG, encoding="utf-8") as fh:
        config = json.load(fh)
    key = args.port.replace("\\", "/").strip("/")
    if key not in config:
        die("%s is not described in scripts/dotnet-ports.json" % key)
    spec = config[key]

    port = Port(key)
    old_version = port.var("DISTVERSION")
    prefix = port.vars.get("DISTVERSIONPREFIX", "")
    new_version = args.version[len(prefix):] if prefix and args.version.startswith(prefix) else args.version
    if new_version == old_version:
        note("already at %s; refreshing anyway" % old_version)
    old_tag, new_tag = port.tag(old_version), port.tag(new_version)
    note("%s: %s -> %s" % (key, old_tag, new_tag))

    old_files = tree_files(port, old_tag)
    new_files = tree_files(port, new_tag)

    added, removed, unexpected = update_plist(port, old_files, new_files, spec["plist_maps"])
    note("pkg-plist: +%d -%d" % (len(added), len(removed)))

    workdir = tempfile.mkdtemp(prefix="dotnet-port-")
    srcdir = args.keep_src or os.path.join(workdir, "src")
    os.makedirs(srcdir, exist_ok=True)
    try:
        tarpath = os.path.join(workdir, "src.tar.gz")
        note("downloading %s" % port.tarball(new_version))
        tar_sha, tar_size = fetch_tarball(port, new_tag, tarpath)
        tree = extract(tarpath, srcdir)

        previous = parse_nupkgs(port.read("Makefile.nuget"))
        old_pkgs = set(previous)
        prunable: set = set()
        if args.packages_dir:
            pkgs = cased_ids(packages_from_dir(args.packages_dir), args.packages_dir)
            source = "packages dir %s" % args.packages_dir
        elif not args.no_restore and sdk_available(args.dotnet):
            pkgs = restore_packages(args.dotnet, tree, spec["restore_project"],
                                    os.path.join(workdir, "packages"))
            source = "dotnet restore"
        elif old_version == new_version:
            die("no .NET SDK, and the old and new tags match, so there is no "
                "delta to walk; pass --packages-dir or install an SDK")
        else:
            note("no .NET SDK found; falling back to walking api.nuget.org")
            oldtar = os.path.join(workdir, "old.tar.gz")
            fetch_tarball(port, old_tag, oldtar)
            old_tree = extract(oldtar, os.path.join(workdir, "old"))
            pkgs, prunable = walk_delta(old_tree, tree, spec["restore_project"], old_pkgs)
            if args.prune:
                pkgs -= prunable
                prunable = set()
            source = "api.nuget.org delta walk (UNVERIFIED)"

        write_nuget_makefile(port, pkgs, previous)
        write_distinfo(port, pkgs, port.tarball(new_version), tar_sha, tar_size)
        bump_makefile(port, new_version)
    finally:
        if not args.keep_src:
            shutil.rmtree(workdir, ignore_errors=True)
        else:
            shutil.rmtree(os.path.join(workdir, "packages"), ignore_errors=True)

    gone = sorted(old_pkgs - pkgs, key=sortkey)
    fresh = sorted(pkgs - old_pkgs, key=sortkey)
    print("\n%s -> %s" % (old_tag, new_tag))
    print("  package set: %d (%s)" % (len(pkgs), source))
    for label, items in (("added", fresh), ("removed", gone)):
        print("  nuget %s (%d):" % (label, len(items)))
        for pid, ver in items:
            print("    %s %s:%s" % ("+-"[label == "removed"], pid, ver))
    for label, items in (("added", added), ("removed", removed)):
        print("  plist %s (%d):" % (label, len(items)))
        for entry in sorted(items):
            print("    %s %s" % ("+-"[label == "removed"], entry))
    if unexpected:
        print("  plist entries dropped that upstream no longer ships (%d):" % len(unexpected))
        for entry in sorted(unexpected):
            print("    ? %s" % entry)
    if prunable:
        print("  nuget the walk no longer reaches, KEPT (%d):" % len(prunable))
        for pid, ver in sorted(prunable, key=sortkey):
            print("    ? %s:%s" % (pid, ver))

    churn = {p.lower() for p, _ in fresh} ^ {p.lower() for p, _ in gone}
    if churn:
        print("\n  note: the package set changed, so the assemblies published into")
        print("  %%DATADIR%% may have changed too. Those pkg-plist lines are build")
        print("  output, not upstream sources, so a build is the only way to confirm.")
    if prunable:
        print("\n  note: the '?' packages above were left in place. The offline walk")
        print("  cannot tell a package that is truly gone from one it fails to reach,")
        print("  and dropping a live one fails the restore with NU1101. A restore")
        print("  (--packages-dir) prunes them exactly; --prune trusts the walk instead.")
    if source.endswith("(UNVERIFIED)"):
        print("\n  note: Makefile.nuget came from an offline dependency walk, not a")
        print("  real restore. Build the port, or rerun with --packages-dir, to confirm.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
