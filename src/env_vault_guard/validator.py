from dataclasses import dataclass, field
from typing import Dict, List, Set
from .parser import EnvParser

WEAK_SECRET_PATTERNS = {
    "123456", "password", "secret", "changeme", "admin", "test",
    "root", "qwerty", "12345678", "dev", "default"
}


@dataclass
class ValidationResult:
    is_valid: bool
    missing_keys: List[str] = field(default_factory=list)
    empty_keys: List[str] = field(default_factory=list)
    undocumented_keys: List[str] = field(default_factory=list)
    weak_secrets: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = []
        if self.is_valid:
            lines.append("✅ Environment variables check PASSED. No drift detected.")
        else:
            lines.append("❌ Environment variables check FAILED.")

        if self.missing_keys:
            lines.append(f"  - Missing keys (in example but not in env): {', '.join(self.missing_keys)}")
        if self.empty_keys:
            lines.append(f"  - Empty values: {', '.join(self.empty_keys)}")
        if self.undocumented_keys:
            lines.append(f"  - Undocumented keys (in env but not in example): {', '.join(self.undocumented_keys)}")
        if self.weak_secrets:
            lines.append(f"  - Warning: Weak/default dummy secrets detected: {', '.join(self.weak_secrets)}")

        return "\n".join(lines)


class EnvValidator:
    """Validates .env completeness against .env.example template and detects secrets drift."""

    def __init__(self, check_weak_secrets: bool = True):
        self.check_weak_secrets = check_weak_secrets

    def compare(self, env_data: Dict[str, str], example_data: Dict[str, str]) -> ValidationResult:
        env_keys = set(env_data.keys())
        example_keys = set(example_data.keys())

        missing = sorted(list(example_keys - env_keys))
        undocumented = sorted(list(env_keys - example_keys))
        empty = sorted([k for k, v in env_data.items() if not str(v).strip()])

        weak = []
        if self.check_weak_secrets:
            for k, v in env_data.items():
                if v.lower() in WEAK_SECRET_PATTERNS:
                    weak.append(k)

        is_valid = len(missing) == 0 and len(empty) == 0

        return ValidationResult(
            is_valid=is_valid,
            missing_keys=missing,
            empty_keys=empty,
            undocumented_keys=undocumented,
            weak_secrets=weak
        )

    def validate_files(self, env_path: str, example_path: str) -> ValidationResult:
        env_data = EnvParser.parse_file(env_path)
        example_data = EnvParser.parse_file(example_path)
        return self.compare(env_data, example_data)
