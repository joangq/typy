from typy import pyright
import rich

result: pyright.Analysis = pyright.run("test/sample_file.py")

rich.print(result)