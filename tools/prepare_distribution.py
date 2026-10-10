#!/usr/bin/env python3
"""Prepare a pinned local distribution; never publish or synchronize repositories."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True).stdout


def safe_path(value):
    p = PurePosixPath(value)
    if p.is_absolute() or not p.parts or any(x in (".", "..") for x in p.parts):
        raise ValueError(f"unsafe path: {value}")
    return p


def prepare(args):
    repo = args.source.resolve()
    if not re.fullmatch(r"[0-9a-f]{40}", args.ref):
        raise ValueError("--ref must be a full, exact source commit SHA")
    sha = git(repo, "rev-parse", "--verify", args.ref + "^{commit}").decode().strip()
    if args.ref != sha:
        raise ValueError("--ref must be a full, exact source commit SHA")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?", args.version):
        raise ValueError("--version must be a semantic version")
    output = args.output.resolve()
    if output.exists():
        raise ValueError("output already exists; choose a new directory")
    if output == repo or repo in output.parents:
        raise ValueError("output must be outside the source repository")

    files = {}
    modes = {}
    with tarfile.open(fileobj=io.BytesIO(git(repo, "archive", sha)), mode="r:") as archive:
        for member in archive.getmembers():
            path = str(safe_path(member.name))
            if member.isdir():
                continue
            if not member.isfile():
                raise ValueError(f"unsupported source entry: {path}")
            files[path] = archive.extractfile(member).read()
            modes[path] = 0o755 if member.mode & 0o111 else 0o644
    config = json.loads(files["distribution/config.json"])
    metadata_path = "plugins/game-studio/.claude-plugin/plugin.json"
    metadata = json.loads(files[metadata_path])
    if metadata["version"] != args.version:
        raise ValueError("version must match the committed plugin metadata")

    approval = None
    if args.approval_record:
        approval = json.loads(args.approval_record.read_text())
        required = ("approved_by", "approved_at", "checks", "observed_result", "limitations")
        if approval.get("source_commit") != sha or approval.get("version") != args.version:
            raise ValueError("approval applies to a different source commit or version")
        if approval.get("approved") is not True or any(not approval.get(k) for k in required):
            raise ValueError("approval must contain the owner's explicit decision and review record")
        if not isinstance(approval["checks"], list) or not isinstance(approval["limitations"], list):
            raise ValueError("approval checks and limitations must be nonempty lists")
    status = "approved" if approval else "candidate"
    tokens = {
        "VERSION": args.version, "SOURCE_SHA": sha, "STATUS": status,
        "SOURCE_REPOSITORY": config["source_repository"],
        "PUBLICATION_REPOSITORY": config["publication_repository"],
    }
    result = {}
    result_modes = {}
    for prefix in config["include"]:
        safe_path(prefix)
        selected = [p for p in files if p == prefix or p.startswith(prefix + "/")]
        if not selected:
            raise ValueError(f"missing configured source: {prefix}")
        for path in selected:
            result[path], result_modes[path] = files[path], modes[path]
    for prefix in config.get("exclude", []):
        safe_path(prefix)
        for path in list(result):
            if path == prefix or path.startswith(prefix + "/"):
                del result[path]
                del result_modes[path]
    for source, target in config["templates"].items():
        safe_path(source)
        safe_path(target)
        if target in result:
            raise ValueError(f"duplicate publication path: {target}")
        text = files[source].decode()
        for name, value in tokens.items():
            text = text.replace("{{" + name + "}}", value)
        if re.search(r"\{\{[A-Z_]+\}\}", text):
            raise ValueError(f"unresolved template token in {source}")
        result[target], result_modes[target] = text.encode(), 0o644
    metadata["repository"] = "https://github.com/" + config["publication_repository"]
    result[metadata_path] = (json.dumps(metadata, indent=2) + "\n").encode()

    manifest = {
        "schema_version": 1, "version": args.version, "status": status,
        "source_repository": config["source_repository"], "source_commit": sha,
        "publication_repository": config["publication_repository"], "approval": approval,
        "files": [{"path": p, "sha256": hashlib.sha256(data).hexdigest(),
                   "git_blob_sha": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest(),
                   "mode": format(result_modes[p], "o")} for p, data in sorted(result.items())],
    }
    output.mkdir(parents=True)
    for path, data in result.items():
        destination = output.joinpath(*safe_path(path).parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        destination.chmod(result_modes[path])
    (output / "RELEASE.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"source_commit": sha, "version": args.version, "status": status,
                      "files": len(result) + 1, "output": str(output)}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path.cwd())
    parser.add_argument("--ref", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--approval-record", type=Path)
    args = parser.parse_args()
    try:
        prepare(args)
    except (KeyError, ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    main()
