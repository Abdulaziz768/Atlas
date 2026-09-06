from dataclasses import dataclass, field


@dataclass
class QualityResult:
    valid: bool
    errors: list[str] = field(default_factory=list)


@dataclass
class QuarantineRecord:
    ticker: str
    errors: list[str]
    record: object