from datetime import datetime, timedelta
from pydantic import BaseModel

class Emitter(BaseModel):
    name: str
    version: None|str

class ReportBase[T: BaseModel](BaseModel):
    issues: list[T]
    elapsed: timedelta
    time: datetime
    emitter: Emitter