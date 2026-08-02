from typing import Any

_DEPLOYMENT_MAP = {
    "aws": "aws",
    "amazon web services": "aws",
    "amazon": "aws",
    "gcp": "gcp",
    "google cloud": "gcp",
    "google cloud platform": "gcp",
    "azure": "azure",
    "microsoft azure": "azure",
    "on prem": "on_prem",
    "on-prem": "on_prem",
    "on_prem": "on_prem",
    "on premises": "on_prem",
    "local": "local",
}

_LICENSE_MAP = {
    "mit": "MIT",
    "apache": "Apache-2.0",
    "apache2": "Apache-2.0",
    "apache-2": "Apache-2.0",
    "apache-2.0": "Apache-2.0",
    "bsd": "BSD",
    "gpl": "GPL",
    "gplv3": "GPLv3",
    "gpl-3.0": "GPLv3",
    "mpl": "MPL",
    "mozilla public license": "MPL",
}

_TRUE_VALUES = {
    "true",
    "yes",
    "y",
    "1",
    "enabled",
    "available",
    "supported",
    "opensource",
    "open source",
    "oss",
    "free",
}

_FALSE_VALUES = {
    "false",
    "no",
    "n",
    "0",
    "disabled",
    "unsupported",
    "closed",
    "commercial",
}


class Normalizer:
    @staticmethod
    def normalize_text(value: Any) -> str | None:
        if value is None:
            return None

        text = str(value).strip()
        return text or None

    @classmethod
    def normalize_deployment(cls, value: Any) -> str | None:
        text = cls.normalize_text(value)
        if text is None:
            return None

        return _DEPLOYMENT_MAP.get(text.lower(), text.lower())

    @classmethod
    def normalize_license(cls, value: Any) -> str | None:
        text = cls.normalize_text(value)
        if text is None:
            return None

        return _LICENSE_MAP.get(text.lower(), text)

    @classmethod
    def normalize_boolean(cls, value: Any) -> bool | None:
        if isinstance(value, bool):
            return value

        text = cls.normalize_text(value)
        if text is None:
            return None

        lowered = text.lower()

        if lowered in _TRUE_VALUES:
            return True

        if lowered in _FALSE_VALUES:
            return False

        return None

    @staticmethod
    def normalize_score(value: Any) -> float | None:
        if not isinstance(value, (int, float)):
            return None

        score = float(value)

        if 1.0 < score <= 100.0:
            score /= 100.0

        return max(0.0, min(1.0, score))

    @staticmethod
    def normalize_number(value: Any) -> float | None:
        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            try:
                return float(value.replace(",", "").strip())
            except ValueError:
                return None

        return None

    @classmethod
    def normalize_list(cls, values: Any) -> list[str]:
        if values is None:
            return []

        if isinstance(values, str):
            values = [values]

        if not isinstance(values, list):
            return []

        normalized: list[str] = []
        seen: set[str] = set()

        for value in values:
            text = cls.normalize_text(value)
            if text is None:
                continue

            lowered = text.lower()
            if lowered in seen:
                continue

            seen.add(lowered)
            normalized.append(text)

        return normalized
