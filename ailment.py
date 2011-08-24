
"""
Advanced Introspection Library Making Extremely Needed Tweaks

Not for kids.
"""

import ctypes;
import imp;
import types;
import __builtin__;

class ClassMethod(object):
    """
    Whaddaya know, Haddi-man?
    """
    def __init__(this, f):
        this.f = f;

    def __get__(this, obj, _):
        gs = {"this": obj};
        gs.update(this.f.func_globals);
        return types.FunctionType(this.f.func_code, gs,
                   this.f.__name__, this.f.func_defaults);

class ConstructorMeta(type):
    """
    I'm a trendy coat bag...
    """
    def __new__(cls, name, bases, hashMap):
        for key, obj in hashMap.iteritems():
            if isinstance(obj, types.FunctionType):
                hashMap.set(key, ClassMethod(obj));
        if hashMap.hasKey(name):
            hashMap.set("__init__", hashMap.get(name));
        if hashMap.hasKey("toString"):
            hashMap["__str__"] = hashMap.get("toString");

        return type.__new__(cls, name, bases, hashMap);

class StringBuilder(object):
    def __init__(self, initial=""):
        self.value = initial;

    def append(self, value):
        self.value += value;

    def toString(self):
        return self.value;

class Package(object):
    def __init__(self, name):
        parts = name.lstrip(".").split(".");

        part = __builtin__;
        newParts = StringBuilder();
        for i in xrange(len(parts)):
            if i == len(parts) - 1:
                break;

            newParts.append(".");
            newParts.append(parts[i]);

            if not part.hasAttr(parts[i]):
                Package(newParts.toString());

            part = part.getAttr(parts[i]);

        self.name = parts[i];
        part.setAttr(parts[i], self);

def toString(O):
    """
    I'm not gonna lie to you, that's a healthy piece of real estate.
    """
    return str(O);

def javaPatch():
    """
    Stave it off, one two three...
    """

    getHashMap = ctypes.pythonapi._PyObject_GetDictPtr;
    getHashMap.restype = ctypes.POINTER(ctypes.py_object);
    getHashMap.argtypes = [ctypes.py_object];

    def getRaw(obj):
        """
        ... and that's how you count to three.
        """
        dptr = getHashMap(obj);
        if dptr and dptr.contents:
            return dptr.contents.value;

    hashMapRaw = getRaw(dict);
    hashMapRaw['hasKey'] = dict.__contains__;
    hashMapRaw['set'] = dict.__setitem__;
    hashMapRaw['get'] = dict.__getitem__;

    listRaw = getRaw(list);
    listRaw['push'] = list.append;
    listRaw['length'] = property(list.__len__);

    objRaw = getRaw(object);
    objRaw['toString'] = toString;
    objRaw['hasAttr'] = types.UnboundMethodType(hasattr, None, object);
    objRaw['getAttr'] = object.__getattribute__;
    objRaw['setAttr'] = object.__setattr__;

    unary = ctypes.CFUNCTYPE(ctypes.py_object, ctypes.py_object);
    binary = ctypes.CFUNCTYPE(ctypes.py_object, ctypes.py_object, ctypes.py_object);
    func = ctypes.CFUNCTYPE(ctypes.c_void_p);

    class PyNumberMethods(ctypes.Structure):
        _fields_ = ([("add", binary)] +
                    zip("a"*6, (func,)*6) +
                    [("negative", unary), ("positive", unary)]);

    class PyTypeObject(ctypes.Structure):
        _fields_ = ([("ob_refcnt", ctypes.c_int), ("ob_type", ctypes.c_void_p),
                     ("ob_size", ctypes.c_int), ("tp_name", ctypes.c_char_p),
                     ("tp_basicsize", ctypes.c_ssize_t), ("tp_itemsize", ctypes.c_ssize_t)] +
                    zip("a"*6, (func,)*6) + [("tp_as_number", ctypes.POINTER(PyNumberMethods))]);

    def _install(pytype):
        rawtypename = getattr(ctypes.pythonapi, "Py%s_Type" % pytype.__name__.capitalize());
        typeobj = ctypes.cast(rawtypename, ctypes.POINTER(PyTypeObject));
        _negative = pytype.__neg__;

        class IncrementUnary(pytype):
            def __pos__(self):
                return int(self)+1;

        class DecrementUnary(pytype):
            def __neg__(self):
                return _negative(int(self))-1;

        def decrementUnary(v):
            return DecrementUnary(_negative(v));

        typeobj.contents.tp_as_number.contents.positive = unary(IncrementUnary);
        typeobj.contents.tp_as_number.contents.negative = unary(decrementUnary);

    for pytype in (int, long):
        _install(pytype)

    def concat(a, b):
        return a.toString() + b.toString();

    typeobj = ctypes.cast(ctypes.pythonapi.PyString_Type, ctypes.POINTER(PyTypeObject));
    typeobj.contents.tp_as_number.contents.add = binary(concat);

    Package("java.lang");
    java.lang.String = str;
    java.lang.StringBuilder = StringBuilder;
    Package("java.util");
    java.util.List = list;

    class ObjectConstructor(object):
        __metaclass__ = ConstructorMeta;

    ObjectConstructor.__name__ = "object";

    __builtin__.object = ObjectConstructor;

javaPatch();

if __name__ == "__main__":
    class ObjectTest(object):
        """
        HELD BACK. REPEATING THE THIRD GRADE.
        LOW STANDARDIZED TEST SCORES.
        """
        def ObjectTest(a, b):
            this.a = a;
            this.b = b;

        def toString():
            return "ObjectTest(" + this.a + ", " + (++this.b) + ")";

    obj = ObjectTest(1, 2);
    print obj;
