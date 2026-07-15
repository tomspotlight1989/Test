"""`--diagnose` command: reports which sources are ready to use right now."""
from __future__ import annotations

import config
from sources import SOURCE_REGISTRY


def run():
    config.load_env()
    print("UK Energy /last30days — source diagnostics\n")
    ready = []
    needs_setup = []
    for name, entry in SOURCE_REGISTRY.items():
        if entry["zero_config"]:
            ready.append((name, entry["label"]))
            continue
        env_var = entry.get("env_var")
        if env_var and config.credential(env_var):
            ready.append((name, entry["label"]))
        else:
            needs_setup.append((name, entry["label"], env_var))

    print(f"Ready now ({len(ready)}):")
    for name, label in ready:
        print(f"  [x] {label} ({name})")

    print(f"\nNeeds setup ({len(needs_setup)}):")
    for name, label, env_var in needs_setup:
        print(f"  [ ] {label} ({name}) — set {env_var}")

    print("\nSee docs/SETUP.md for how to obtain each credential.")
