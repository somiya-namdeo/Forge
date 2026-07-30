import os
import re
import sys
import logging
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Any

# Ensure project root directory is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import BASE_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define Regex Patterns and corresponding Replacement Placeholders
REPLACEMENT_RULES: List[Tuple[str, re.Pattern, str]] = [
    (
        "Private Key",
        re.compile(r"-----BEGIN (?:RSA |EC |PGP |OPENSSH |DSA )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |PGP |OPENSSH |DSA )?PRIVATE KEY-----"),
        "<PRIVATE_KEY_REMOVED>"
    ),
    (
        "Authorization Header",
        re.compile(r"Authorization:\s*Bearer\s+[a-zA-Z0-9_\-\.]{15,}", re.IGNORECASE),
        "Authorization: Bearer <TOKEN>"
    ),
    (
        "Bearer Token",
        re.compile(r"Bearer\s+eyJ[a-zA-Z0-9_\-\.]{15,}", re.IGNORECASE),
        "Bearer <TOKEN>"
    ),
    (
        "Google API Key",
        re.compile(r"AIzaSy[a-zA-Z0-9_\-]{33}"),
        "<GOOGLE_API_KEY>"
    ),
    (
        "OpenAI API Key",
        re.compile(r"sk-(?:proj-|admin-|user-)?(?:progress-|[a-zA-Z0-9_-]{20,})"),
        "<OPENAI_API_KEY>"
    ),
    (
        "Anthropic API Key",
        re.compile(r"sk-ant-[a-zA-Z0-9_-]{20,}"),
        "<ANTHROPIC_API_KEY>"
    ),
    (
        "GitHub Token",
        re.compile(r"(?:ghp|gho|ghu|ghs|ghr|github_pat)_[a-zA-Z0-9_]{36,255}"),
        "<GITHUB_TOKEN>"
    ),
    (
        "PostHog Project Key",
        re.compile(r"phc_[a-zA-Z0-9_\-]{32,64}"),
        "<POSTHOG_PROJECT_KEY>"
    ),
    (
        "PostHog / Public Key",
        re.compile(r"pk_[a-zA-Z0-9_\-]{20,64}"),
        "<POSTHOG_PUBLIC_KEY>"
    ),
    (
        "AWS Access Key",
        re.compile(r"(?:AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}"),
        "<AWS_ACCESS_KEY>"
    ),
    (
        "JWT Token",
        re.compile(r"eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}"),
        "<JWT_TOKEN>"
    ),
    (
        "Session Cookie",
        re.compile(r"session=[a-zA-Z0-9_\-]{20,}", re.IGNORECASE),
        "session=<SESSION_COOKIE>"
    ),
    (
        "HuggingFace Token",
        re.compile(r"hf_[a-zA-Z0-9]{34,}"),
        "<HUGGINGFACE_TOKEN>"
    ),
    (
        "Slack Token",
        re.compile(r"xox[baprs]-[a-zA-Z0-9-]+"),
        "<SLACK_TOKEN>"
    ),
    (
        "Stripe Key",
        re.compile(r"[sr]k_(?:live|test)_[a-zA-Z0-9]{24,}"),
        "<STRIPE_API_KEY>"
    ),
]

EXCLUDE_DIRS = {".git", ".venv", "qdrant", "__pycache__", "node_modules", ".gemini"}
EXCLUDE_EXTS = {".npy", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".tar", ".gz", ".lock", ".pck", ".pyc", ".sqlite", ".db"}


def sanitize_file(file_path: Path) -> Dict[str, int]:
    """
    Sanitizes secrets in a single file, maintaining exact encoding.
    Returns a dictionary of secret counts replaced in this file.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        logger.warning(f"Could not read file {file_path}: {e}")
        return {}

    modified = False
    file_stats = defaultdict(int)

    new_content = content
    for name, pattern, placeholder in REPLACEMENT_RULES:
        matches = pattern.findall(new_content)
        if matches:
            count = len(matches)
            file_stats[name] += count
            new_content = pattern.sub(placeholder, new_content)
            modified = True

    if modified:
        try:
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                f.write(new_content)
        except Exception as e:
            logger.error(f"Failed to write sanitized content to {file_path}: {e}")
            return {}

    return dict(file_stats)


def sanitize_knowledge_base(target_dir: Optional[Path] = None) -> Tuple[List[str], Dict[str, int], int]:
    
    if target_dir is None:
        target_dir = BASE_DIR / "knowledge_base"

    target_dir = Path(target_dir)
    if not target_dir.exists():
        logger.error(f"Target directory does not exist: {target_dir}")
        raise FileNotFoundError(f"Target directory not found: {target_dir}")

    logger.info(f"Starting secret sanitization in {target_dir}...")

    modified_files: List[str] = []
    total_stats: Dict[str, int] = defaultdict(int)
    total_secrets_count = 0

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in EXCLUDE_EXTS:
                continue

            file_stats = sanitize_file(file_path)
            if file_stats:
                rel_path = str(file_path.relative_to(BASE_DIR))
                modified_files.append(rel_path)
                for secret_type, count in file_stats.items():
                    total_stats[secret_type] += count
                    total_secrets_count += count

    logger.info("Sanitization complete.")
    logger.info(f"Total modified files: {len(modified_files)}")
    logger.info(f"Total secrets replaced: {total_secrets_count}")
    for secret_type, count in total_stats.items():
        logger.info(f"  - {secret_type}: {count}")

    return modified_files, dict(total_stats), total_secrets_count


def main() -> None:
    modified_files, total_stats, total_count = sanitize_knowledge_base()
    print("\n" + "=" * 60)
    print("SECRET SANITIZATION REPORT")
    print("=" * 60)
    print(f"Total Secrets Replaced: {total_count}")
    print(f"Total Files Modified  : {len(modified_files)}\n")

    print("Secret Breakdown by Type:")
    print("-" * 60)
    for stype, scount in total_stats.items():
        print(f"  {stype:<25}: {scount}")

    print("\nModified Files List:")
    print("-" * 60)
    for f in modified_files:
        print(f"  {f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
