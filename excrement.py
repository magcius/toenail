
"""
excrement.py
"""

import ctypes

def _install_excrement():
    unary = ctypes.CFUNCTYPE(ctypes.py_object, ctypes.py_object)
    func = ctypes.CFUNCTYPE(ctypes.c_void_p)

    class PyNumberMethods(ctypes.Structure):
        _fields_ = zip("a"*7, (func,)*7) + [("negative", unary), ("positive", unary)]

    class PyTypeObject(ctypes.Structure):
        _fields_ = ([("ob_refcnt", ctypes.c_int), ("ob_type", ctypes.c_void_p),
                     ("ob_size", ctypes.c_int), ("tp_name", ctypes.c_char_p),
                     ("tp_basicsize", ctypes.c_ssize_t), ("tp_itemsize", ctypes.c_ssize_t)] +
                    zip("a"*6, (func,)*6) + [("tp_as_number", ctypes.POINTER(PyNumberMethods))])

    def _install(pytype):
        rawtypename = getattr(ctypes.pythonapi, "Py%s_Type" % pytype.__name__.capitalize())
        typeobj = ctypes.cast(rawtypename, ctypes.POINTER(PyTypeObject))
        _negative = pytype.__neg__

        class IncrementUnary(pytype):
            def __pos__(self):
                return int(self)+1

        class DecrementUnary(pytype):
            def __neg__(self):
                return _negative(int(self))-1

        def decrement_unary(v):
            return DecrementUnary(_negative(v))

        typeobj.contents.tp_as_number.contents.positive = unary(IncrementUnary)
        typeobj.contents.tp_as_number.contents.negative = unary(decrement_unary)

    for pytype in (int, long):
        _install(pytype)

_install_excrement()

a = 1
print ++a

a = 5
print --a
