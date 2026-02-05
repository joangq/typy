from . import issue
from .report import ReportBase

Issue = issue.GitlabIssue

class Report(ReportBase[Issue]): ...