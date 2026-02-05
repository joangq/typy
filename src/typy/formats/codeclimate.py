from . import issue
from .report import ReportBase

Issue = issue.Codeclimate

class Report(ReportBase[Issue]): ...