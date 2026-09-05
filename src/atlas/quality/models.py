from dataclasses import dataclass

@dataclass
class QuarantineRecord:
    ticker : str
    errors : list[str]
    record : object