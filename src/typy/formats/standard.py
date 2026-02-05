from . import issue
from .report import ReportBase

Issue = issue.BaseIssue

class Report(ReportBase[Issue]): ...