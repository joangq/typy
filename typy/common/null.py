class Null(object): ...
NULL = Null()
def disallow_init(self, *_, **__): raise TypeError("Cannot instantiate Null")
Null.__init__ = disallow_init