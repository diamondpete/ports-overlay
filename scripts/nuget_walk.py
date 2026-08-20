"""Offline approximation of the package set `dotnet restore` downloads.

Talks to api.nuget.org's flat container only, so it needs no .NET SDK.  This is
a fallback: `dotnet restore` remains authoritative (see read_assets()).
"""

from __future__ import annotations

import functools
import json
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

FLAT = "https://api.nuget.org/v3-flatcontainer"
UA = {"User-Agent": "ports-overlay-update/1"}
WORKERS = 16


def _fetch(url: str) -> bytes | None:
    req = urllib.request.Request(url, headers=UA)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            if attempt == 2:
                raise
        except OSError:
            if attempt == 2:
                raise
    return None


# ---------------------------------------------------------------- versions


def vkey(v: str):
    """NuGet SemVer2 ordering key; tolerates 4-part and prerelease versions."""
    v = v.strip().split("+")[0]
    core, _, pre = v.partition("-")
    nums = [int(x) for x in core.split(".") if x.isdigit()]
    nums += [0] * (4 - len(nums))
    if not pre:
        return (tuple(nums[:4]), (1,))
    parts = [(0, int(p), "") if p.isdigit() else (1, 0, p.lower()) for p in pre.split(".")]
    return (tuple(nums[:4]), (0, tuple(parts)))


class Range:
    """A NuGet version range: '1.0.0', '[1.0.0]', '[1.0.0, 2.0.0)', '*'."""

    __slots__ = ("lo", "hi", "lo_inc", "hi_inc", "spec")

    def __init__(self, spec: str):
        spec = self.spec = (spec or "").strip()
        self.lo = self.hi = None
        self.lo_inc, self.hi_inc = True, False
        if not spec or spec == "*":
            return
        if spec[0] in "[(":
            self.lo_inc, self.hi_inc = spec[0] == "[", spec[-1] == "]"
            body = spec[1:-1]
            if "," in body:
                lo, hi = body.split(",", 1)
                self.lo, self.hi = lo.strip() or None, hi.strip() or None
            else:
                self.lo = self.hi = body.strip()
                self.lo_inc = self.hi_inc = True
        else:
            self.lo = spec

    def contains(self, v: str) -> bool:
        k = vkey(v)
        if self.lo is not None:
            lk = vkey(self.lo)
            if k < lk or (k == lk and not self.lo_inc):
                return False
        if self.hi is not None:
            hk = vkey(self.hi)
            if k > hk or (k == hk and not self.hi_inc):
                return False
        return True

    @property
    def is_simple_min(self) -> bool:
        return self.lo is not None and self.hi is None and self.lo_inc


# ---------------------------------------------------------------- frameworks

_ALIASES = {
    ".netstandard": "netstandard",
    ".netcoreapp": "netcoreapp",
    ".netframework": "net",
    ".netplatform": "netstandard",
    "netcore": "netcoreapp",
    "dotnet": "netstandard",
}


def norm_tfm(raw: str) -> str:
    """'.NETFramework4.7.1' -> 'net471'; '.NETStandard2.0' -> 'netstandard2.0'."""
    s = (raw or "").strip().split(",")[0].lower()
    if not s:
        return "any"
    m = re.match(r"^([a-z.]+?)\s*v?([0-9][0-9.]*)?$", s)
    if not m:
        return s
    fam, ver = _ALIASES.get(m.group(1), m.group(1).lstrip(".")), m.group(2) or ""
    if fam == "net" and ver:
        parts = ver.split(".")
        if len(parts) > 1 and int(parts[0]) >= 5:
            return "net%s.%s" % (parts[0], parts[1])
        return "net" + ver.replace(".", "")
    if fam in ("netstandard", "netcoreapp") and ver:
        if "." not in ver:
            ver = ver[0] + "." + ver[1:]
        return fam + ver
    return fam + ver


_NS = ["netstandard%s" % v for v in ("2.1", "2.0", "1.6", "1.5", "1.4", "1.3", "1.2", "1.1", "1.0")]
_FX = ["net481", "net48", "net472", "net471", "net47", "net462", "net461", "net46",
       "net452", "net451", "net45", "net40", "net35", "net20", "net11"]
_CORE = ["3.1", "3.0", "2.2", "2.1", "2.0", "1.1", "1.0"]


@functools.lru_cache(maxsize=None)
def compat_chain(tfm: str) -> tuple:
    """Dependency-group frameworks `tfm` can consume, best match first."""
    tfm = norm_tfm(tfm)
    out: list[str] = []
    m = re.match(r"^net(\d+)\.(\d+)$", tfm)
    if m:  # net5.0 and later
        major, minor = int(m.group(1)), int(m.group(2))
        for ma in range(major, 4, -1):
            for mi in range(minor if ma == major else 9, -1, -1):
                out.append("net%d.%d" % (ma, mi))
        out += ["netcoreapp" + v for v in _CORE] + _NS
    elif tfm.startswith("netcoreapp"):
        ver = tfm[len("netcoreapp"):]
        out += ["netcoreapp" + v for v in _CORE if vkey(v) <= vkey(ver)]
        out += _NS if vkey(ver) >= vkey("3.0") else _NS[1:]
    elif tfm.startswith("netstandard"):
        ver = tfm[len("netstandard"):]
        out += [f for f in _NS if vkey(f[len("netstandard"):]) <= vkey(ver)]
    elif tfm in _FX:
        out += _FX[_FX.index(tfm):]
        out += _NS[1:] if vkey(tfm[3:]) >= vkey("461") else _NS[2:]
    else:
        out.append(tfm)
    return tuple(out + ["any"])


# ---------------------------------------------------------------- registry


@functools.lru_cache(maxsize=None)
def versions(pkg_id: str) -> tuple:
    body = _fetch("%s/%s/index.json" % (FLAT, pkg_id.lower()))
    return tuple(json.loads(body)["versions"]) if body else ()


@functools.lru_cache(maxsize=None)
def nuspec(pkg_id: str, version: str):
    lid, lv = pkg_id.lower(), version.lower()
    body = _fetch("%s/%s/%s/%s.nuspec" % (FLAT, lid, lv, lid))
    return ET.fromstring(body) if body else None


def resolve_version(pkg_id: str, rng: Range) -> str | None:
    """NuGet picks the *lowest* published version satisfying the range."""
    if rng.is_simple_min and nuspec(pkg_id, rng.lo) is not None:
        return rng.lo
    cands = [v for v in versions(pkg_id) if rng.contains(v)]
    if not cands:
        return None
    stable = [v for v in cands if "-" not in v]
    return min(stable or cands, key=vkey)


def deps_for(pkg_id: str, version: str, tfm: str) -> list:
    """[(id, Range)] from the nearest-compatible dependency group."""
    spec = nuspec(pkg_id, version)
    if spec is None:
        return []
    node = None
    for el in spec.iter():
        if el.tag.split("}")[-1] == "dependencies":
            node = el
            break
    if node is None:
        return []
    groups: dict[str, list] = {}
    flat: list = []
    for child in node:
        tag = child.tag.split("}")[-1]
        if tag == "group":
            fw = norm_tfm(child.get("targetFramework", ""))
            groups.setdefault(fw, [])
            groups[fw] += [(d.get("id"), Range(d.get("version", "")))
                           for d in child if d.tag.split("}")[-1] == "dependency"]
        elif tag == "dependency":
            flat.append((child.get("id"), Range(child.get("version", ""))))
    if not groups:
        return flat
    for cand in compat_chain(tfm):
        if cand in groups:
            return groups[cand]
    return []


# ---------------------------------------------------------------- walk

# Shipped inside the shared framework, never restored as a .nupkg.
SUPPRESSED = {"microsoft.netcore.app", "microsoft.aspnetcore.app", "microsoft.netcore.app.ref",
              "microsoft.aspnetcore.app.ref", "netstandard.library.ref"}


def walk(roots: list, tfm: str, warn=lambda m: None) -> set:
    """Every (id, version) restore visits for one project/TFM pair.

    NuGet fetches each version it walks, not only the ones that survive
    conflict resolution, so eclipsed versions belong in DISTFILES too.  A
    package named directly by the project pins that id outright: transitive
    requests for it are dropped without being resolved.
    """
    pinned = {pid.lower() for pid, _ in roots}
    out: set = set()
    seen: set = set()
    level, depth = roots, 0
    while level and depth <= 60:
        pending = {}
        for pid, rng in level:
            lid = pid.lower()
            if lid in SUPPRESSED or (depth and lid in pinned):
                continue
            pending.setdefault((lid, rng.spec), (pid, rng))
        if not pending:
            break
        fresh = set()
        with ThreadPoolExecutor(WORKERS) as ex:
            futs = {ex.submit(resolve_version, pid, rng): pid for pid, rng in pending.values()}
            for fut in futs:
                pid, v = futs[fut], fut.result()
                if v is None:
                    warn("no version of %s satisfies its range" % pid)
                elif (pid.lower(), v) not in seen:
                    fresh.add((pid, v))
        nxt: list = []
        with ThreadPoolExecutor(WORKERS) as ex:
            futs = {ex.submit(deps_for, pid, v, tfm): (pid, v) for pid, v in fresh}
            for fut in futs:
                pid, v = futs[fut]
                seen.add((pid.lower(), v))
                out.add((pid, v))
                nxt += fut.result()
        level, depth = nxt, depth + 1
    if depth > 60:
        warn("dependency walk hit its depth limit")
    return out


# ---------------------------------------------------------------- projects

_COND = re.compile(r"'\$\(TargetFramework\)'\s*(==|!=)\s*'([^']*)'")


def project_tfms(proj: ET.Element) -> list:
    for tag in ("TargetFrameworks", "TargetFramework"):
        el = proj.find(".//" + tag)
        if el is not None and el.text:
            return [norm_tfm(t) for t in el.text.split(";") if t.strip()]
    return []


def package_refs(proj: ET.Element, tfm: str) -> list:
    """PackageReference items live under ItemGroups that may be TFM-gated."""
    out = []
    for ig in proj.iter():
        if ig.tag.split("}")[-1] != "ItemGroup":
            continue
        m = _COND.search(ig.get("Condition", ""))
        if m and (m.group(1) == "==") != (norm_tfm(m.group(2)) == tfm):
            continue
        out += [(c.get("Include"), Range(c.get("Version", "")))
                for c in ig if c.tag.split("}")[-1] == "PackageReference" and c.get("Include")]
    return out


def project_refs(proj: ET.Element) -> list:
    return [c.get("Include").replace("\\", "/")
            for c in proj.iter() if c.tag.split("}")[-1] == "ProjectReference" and c.get("Include")]
