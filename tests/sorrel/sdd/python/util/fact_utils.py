import os

def read_facts(filename):
    facts = {}
    target_path = ""

    # 1. Check environment variable
    env_dir = os.environ.get("SORREL_FACTS_DIR")
    if env_dir:
        p = os.path.join(env_dir, filename)
        if os.path.exists(p):
            target_path = p

    # 2. Search heuristic
    if not target_path:
        search_dirs = [
            "facts",
            "../facts",
            "../../facts",
            "tests/sorrel/sdd/facts"
        ]
        for dir in search_dirs:
            p = os.path.join(dir, filename)
            if os.path.exists(p):
                target_path = p
                break

    if not target_path:
        target_path = filename

    try:
        with open(target_path, 'r') as f:
            for line in f:
                trimmed = line.strip()
                if not trimmed or trimmed.startswith('#') or trimmed.startswith("Situation:"):
                    continue

                parts = trimmed.split(' ', 1)
                if len(parts) < 2:
                    continue

                rest = parts[1].strip()
                if '=' in rest:
                    key, value = rest.split('=', 1)
                    facts[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"Error: Could not read facts for '{filename}'")

    return facts
