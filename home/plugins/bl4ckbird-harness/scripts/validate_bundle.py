#!/usr/bin/env python3
"""Check the portable bundle structure without optional dependencies."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


SKILLS = {
    "using-harness", "harness-discover", "harness-design", "harness-roadmap",
    "harness-spec", "harness-plan", "harness-execute", "harness-review",
    "harness-diagnose", "harness-finish",
}
PROMPTS = {
    "discovery", "design", "roadmap", "spec", "plan", "implementation",
    "final", "re-review",
}
RUNTIME_MODULES = (
    "records",
    "harness_records",
    "harness_records.capture",
    "harness_records.cli",
    "harness_records.errors",
    "harness_records.files",
    "harness_records.identifiers",
    "harness_records.recovery",
    "harness_records.repair",
    "harness_records.schema",
    "harness_records.state",
    "harness_records.store",
)
RUNTIME_IMPORT = """
import importlib
import sys
from pathlib import Path

scripts = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(scripts))
for name in sys.argv[2:]:
    module = importlib.import_module(name)
    Path(module.__file__).resolve().relative_to(scripts)
"""


def contained(path, root):
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def validate_runtime(root):
    scripts = root / "scripts"
    errors = []
    for module in RUNTIME_MODULES:
        source = scripts.joinpath(*module.split("."))
        source = source.with_suffix(".py") if module != "harness_records" else source / "__init__.py"
        if not source.is_file():
            errors.append("Missing runtime module: " + str(source.relative_to(root)))
    if errors:
        return errors
    try:
        result = subprocess.run(
            [sys.executable, "-B", "-I", "-c", RUNTIME_IMPORT, str(scripts), *RUNTIME_MODULES],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return ["Timed out loading runtime modules"]
    except OSError as error:
        return ["Cannot start runtime module check: " + str(error)]
    if result.returncode:
        detail = (result.stderr or result.stdout).strip().splitlines()
        errors.append("Cannot load runtime modules" + (
            ": " + detail[-1] if detail else ""
        ))
    return errors


def validate(root):
    root = Path(root).resolve()
    errors = []
    for path in root.rglob("*"):
        if path.is_symlink():
            errors.append("Symlink requires explicit packaging review: " + str(path.relative_to(root)))
    if errors:
        return errors
    errors.extend(validate_runtime(root))
    manifest_path = root / ".codex-plugin/plugin.json"
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, ValueError) as exc:
        return ["Cannot read plugin manifest: " + str(exc)]
    if not isinstance(manifest, dict):
        return ["Plugin manifest must be an object"]
    if manifest.get("name") != "bl4ckbird-harness":
        errors.append("Unexpected plugin manifest identity")
    for key in ("name", "version", "description"):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            errors.append("Missing manifest string: " + key)
    version = manifest.get("version", "")
    if isinstance(version, str) and not re.fullmatch(
        r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
        r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
        r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?", version
    ):
        errors.append("Manifest version is not semantic versioning")
    for field in ("author", "interface"):
        if not isinstance(manifest.get(field), dict):
            errors.append("Missing manifest object: " + field)
    author = manifest.get("author", {})
    if isinstance(author, dict) and (
        not isinstance(author.get("name"), str) or not author["name"].strip()
    ):
        errors.append("Missing author name")
    interface = manifest.get("interface", {})
    if isinstance(interface, dict):
        for key in ("displayName", "shortDescription", "longDescription",
                    "developerName", "category", "defaultPrompt"):
            if not isinstance(interface.get(key), str) or not interface[key].strip():
                errors.append("Missing interface string: " + key)
        capabilities = interface.get("capabilities")
        if not isinstance(capabilities, list) or any(
            not isinstance(item, str) or not item.strip() for item in capabilities
        ):
            errors.append("Invalid interface capabilities")
    for key in ("skills", "apps", "mcpServers"):
        raw = manifest.get(key)
        if raw is None:
            continue
        if key == "mcpServers" and isinstance(raw, dict):
            continue
        if not isinstance(raw, str) or Path(raw).is_absolute():
            errors.append("Invalid manifest path: " + key)
        elif not contained(root / raw, root) or not (root / raw).exists():
            errors.append("Missing or external manifest path: " + key)
    actual = {p.parent.name for p in (root / "skills").glob("*/SKILL.md")}
    if actual != SKILLS:
        errors.append("Skill inventory differs: " + str(sorted(actual ^ SKILLS)))
    for name in sorted(actual):
        path = root / "skills" / name / "SKILL.md"
        contents = path.read_text()
        match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", contents, re.S)
        if not match:
            errors.append("Missing skill frontmatter: " + name)
            continue
        fields = {}
        for line in match.group(1).splitlines():
            key, separator, value = line.partition(":")
            if not separator or key not in {"name", "description"} or key in fields:
                errors.append("Unsupported frontmatter; use official YAML validator: " + name)
                continue
            fields[key] = value.strip()
        if fields.get("name") != name or not fields.get("description"):
            errors.append("Invalid skill name or description: " + name)
    prompts = root / "skills/harness-review/references/prompts"
    actual_prompts = {p.stem for p in prompts.glob("*.md")}
    if actual_prompts != PROMPTS:
        errors.append("Review prompt inventory differs: " + str(sorted(actual_prompts ^ PROMPTS)))
    for path in (root / "skills").rglob("*.md"):
        contents = path.read_text()
        links = re.findall(r"\]\(([^)]+)\)", contents)
        links += re.findall(r"(?m)^\s*\[[^\]]+\]:\s*(\S+)", contents)
        for raw in links:
            raw = raw.strip().split(' "', 1)[0].strip("<>")
            target = urlsplit(raw)
            if target.scheme in {"https", "http", "mailto"}:
                continue
            if target.scheme:
                errors.append("Unsupported link scheme: " + str(path.relative_to(root)))
                continue
            if not target.path:
                continue
            resolved = path.parent / unquote(target.path)
            if not contained(resolved, root):
                errors.append("Reference escapes bundle: " + str(path.relative_to(root)) + " -> " + raw)
            elif not resolved.exists():
                errors.append("Missing reference: " + str(path.relative_to(root)) + " -> " + raw)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.bundle)
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
