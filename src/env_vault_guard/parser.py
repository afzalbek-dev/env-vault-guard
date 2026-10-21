import os
import re
from typing import Dict, List, Optional, Tuple


class EnvParser:
    """Robust parser for .env and .env.example files."""

    @staticmethod
    def parse_text(content: str) -> Dict[str, str]:
        env_dict: Dict[str, str] = {}
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()

                if key.startswith("export "):
                    key = key[7:].strip()

                # Remove matching surrounding quotes
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                else:
                    # Strip unquoted inline comments
                    if " #" in val:
                        val = val.split(" #", 1)[0].strip()

                env_dict[key] = val
        return env_dict

    @classmethod
    def parse_file(cls, filepath: str) -> Dict[str, str]:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            return cls.parse_text(f.read())

    @staticmethod
    def dump(env_dict: Dict[str, str]) -> str:
        lines: List[str] = []
        for k, v in sorted(env_dict.items()):
            if " " in v or "\n" in v:
                lines.append(f'{k}="{v}"')
            else:
                lines.append(f"{k}={v}")
        return "\n".join(lines) + "\n"
