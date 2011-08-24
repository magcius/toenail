
"""
Generic Web Framework Abstraction Layer
"""

from twisted.application.internet import TCPServer   as T
import ast                                           as O
from sys import exit                                 as E
from twisted.application.app import startApplication as N
from twisted.application.service import Application  as A
from inspect import currentframe as C, getabsfile    as I
from twisted.web.resource import Resource            as L
from twisted.web.server import Site                  as S

class a(object):
    def __init__(self, t):
        self._s = t

    def __getattr__(self, n):
        if n[0] == "_":
            return object.__getattribute__(self, n)
        if n in self._s.args:
            return self._s.args[n][0]
        return None

def b(a, c, d):
    e = a.split('/')
    for f in e[:-1]:
        if f == '': continue
        if f not in d.children:
            m = L()
            d.putChild(f, m)
        d = d.children[f]
    d.putChild(e[-1], c())

def c(a, b):
    class D(O.NodeTransformer):
        def visit_With(self, n):
            r = n.context_expr
            if isinstance(r, O.Call) and len(r.args) == 1 and r.func.id in ("get", "post"):
                render_method = O.FunctionDef(
                    "render_" + r.func.id.upper(),
                    O.arguments([
                            O.Name("self", O.Param()),
                            O.Name(n.optional_vars.id if n.optional_vars else "request",
                                     O.Param())],
                                  None, None, []),
                    [O.Assign([O.Subscript(O.Call(O.Name("globals",O.Load()), [], [], None, None),
                                               O.Index(O.Str("_GWFAL_response")), O.Store())],
                                O.Str("")),
                     O.Assign([O.Name("request", O.Store())],
                                O.Call(O.Attribute(O.Name("_GWFAL",O.Load()), "a", O.Load()),
                                          [O.Name("request", O.Load())], [], None, None))]
                    + n.body +
                    [O.Return(O.Name("_GWFAL_response", O.Load()))], [])

                return [O.ClassDef("GWFAL_Resource_"+r.args[0].s,
                                     [O.Attribute(O.Name("_GWFAL_twr", O.Load()), "Resource", O.Load())],
                                     [render_method], []),
                        O.Expr(O.Call(O.Attribute(O.Name("_GWFAL", O.Load()), "b", O.Load()),
                                          [r.args[0], O.Name("GWFAL_Resource_"+r.args[0].s,
                                                                  O.Load()), O.Name("_GWFAL_root",O.Load())],
                                          [], None, None))]

        def visit_Module(self, n):

            L = [
                O.Import([O.alias("twisted.web.resource", "_GWFAL_twr")]),
                O.Import([O.alias("gwfal", "_GWFAL")]),
                O.Assign([O.Name("_GWFAL_root", O.Store())],
                           O.Call(O.Attribute(O.Name("_GWFAL_twr", O.Load()), "Resource", O.Load()), [], [], None, None)),
                ]

            for c in n.body:
                c = self.visit(c)
                if isinstance(c, O.AST):
                    L.append(O.fix_missing_locations(c))
                else:
                    L.extend(O.fix_missing_locations(s) for s in c)

            L.append(O.Expr(
                    O.Call(O.Attribute(O.Name("_GWFAL", O.Load()), "_", O.Load()),
                             [O.Num(b), O.Name("_GWFAL_root", O.Load())],
                             [], None, None)))
            return O.Module([O.fix_missing_locations(a) for a in L])

    return D().visit(a)

def _(p, d):
    print ">>> GWFAL is listening on 0.0.0.0:" + str(p)
    a = A("Generic Web Framework Abstraction Layer")
    T(p, S(d)).setServiceParent(a)
    N(a, False)
    r()

def respond(value):
    C(1).f_globals["_GWFAL_response"] += value

get = post = request = None

__all__ = ['get', 'post', 'respond', 'request']

def r():
    n = C()
    while n.f_back: n = n.f_back
    exec compile(c(O.parse(open(I(n)).read()), n.f_globals.get('PORT', 8080)), I(n), "exec") in {}
    E(0)

r()
