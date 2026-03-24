from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_FILE = PROJECT_ROOT / "project_dump.txt"

EXCLUDE_DIRS = {
    "venv",
    ".venv",
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    "dist",
    "build",
    "staticfiles",
    "migrations",
}

EXCLUDE_FILES = {
    "db.sqlite3",
    "project_dump.txt",
    "dump_project.py",
}

INCLUDE_EXTENSIONS = {
    ".py",
    ".html",
    ".css",
    ".js",
    ".txt",
    ".md",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
}

def should_skip(path: Path) -> bool:
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True
    if path.name in EXCLUDE_FILES:
        return True
    return False

def build_tree(root: Path):
    lines = []

    def walk(current: Path, prefix=""):
        items = sorted(
            [p for p in current.iterdir() if not should_skip(p)],
            key=lambda p: (p.is_file(), p.name.lower())
        )

        for i, item in enumerate(items):
            connector = "└── " if i == len(items) - 1 else "├── "
            lines.append(prefix + connector + item.name)
            if item.is_dir():
                extension = "    " if i == len(items) - 1 else "│   "
                walk(item, prefix + extension)

    lines.append(root.name)
    walk(root)
    return "\n".join(lines)

def dump_files(root: Path):
    chunks = []

    files = sorted(
        [
            p for p in root.rglob("*")
            if p.is_file()
            and not should_skip(p)
            and p.suffix.lower() in INCLUDE_EXTENSIONS
        ],
        key=lambda p: str(p).lower()
    )

    for file_path in files:
        relative = file_path.relative_to(root)
        chunks.append("\n" + "=" * 100)
        chunks.append(f"FILE: {relative}")
        chunks.append("=" * 100)

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = file_path.read_text(encoding="cp1251")
            except Exception as e:
                content = f"[ERROR READING FILE: {e}]"
        except Exception as e:
            content = f"[ERROR READING FILE: {e}]"

        chunks.append(content)

    return "\n".join(chunks)

def main():
    tree = build_tree(PROJECT_ROOT)
    files_dump = dump_files(PROJECT_ROOT)

    output = []
    output.append("PROJECT STRUCTURE")
    output.append("=" * 100)
    output.append(tree)
    output.append("\n\nPROJECT FILES")
    output.append("=" * 100)
    output.append(files_dump)

    OUTPUT_FILE.write_text("\n".join(output), encoding="utf-8")
    print(f"Готово: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()