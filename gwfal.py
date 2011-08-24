
"""
Generic Web Framework Abstraction Layer
"""

import sys
import ast
import inspect

from twisted.internet import reactor
from twisted.web import server
from twisted.application import internet, service, app

class _wrap_request(object):
    def __init__(self, tr):
        self._s = tr

    def __getattr__(self, n):
        if n[0] == "_":
            return object.__getattribute__(self, n)
        if n in self._s.args:
            return self._s.args[n][0]
        return None

def _put_resource(path, resource, ctx):
    L = path.split('/')
    for s in L[:-1]:
        if s == '': continue
        if s not in ctx.children:
            m = resource.Resource()
            ctx.putChild(s, m)
        ctx = ctx.children[s]
    ctx.putChild(L[-1], resource())

def _transform_ast(AST, port):
    def load_name(name):
        return ast.Name(name, ast.Load())
    def load_attrib(obj, attr):
        return ast.Attribute(load_name(obj), attr, ast.Load())
    class GWFALNodeTransformer(ast.NodeTransformer):
        def visit_With(self, node):
            request_name = node.optional_vars.id if node.optional_vars else "request"
            expr = node.context_expr
            if isinstance(expr, ast.Call) and len(expr.args) == 1 and expr.func.id in ("get", "post"):
                route_name = "GWFAL_Resource_"+expr.args[0].s
                http_method = expr.func.id.upper()

                render_method = ast.FunctionDef(
                    "render_" + http_method,
                    ast.arguments([
                            ast.Name("self", ast.Param()),
                            ast.Name(request_name, ast.Param())],
                                  None, None, []),
                    # globals()['_GWFAL_response'] = ''
                    [ast.Assign([ast.Subscript(ast.Call(load_name("globals"), [], [], None, None),
                                               ast.Index(ast.Str("_GWFAL_response")), ast.Store())],
                                ast.Str("")),
                    # request = _GWFAL._wrap_response(request)
                     ast.Assign([ast.Name("request", ast.Store())],
                                ast.Call(load_attrib("_GWFAL", "_wrap_request"),
                                          [load_name("request")], [], None, None))]
                    + node.body +
                    # return _GWFAL_response
                    [ast.Return(load_name("_GWFAL_response"))], [])

                return [ast.ClassDef(route_name,
                                     [load_attrib("_GWFAL_twr", "Resource")],
                                     [render_method], []),
                        ast.Expr(ast.Call(load_attrib("_GWFAL", "_put_resource"),
                                          [expr.args[0], load_name(route_name), load_name("_GWFAL_root")],
                                          [], None, None))]

        def visit_Module(self, node):
            L = [
                # import twisted.web.resource as _GWFAL_twr
                ast.Import([ast.alias("twisted.web.resource", "_GWFAL_twr")]),
                # import gwfal as _GWFAL
                ast.Import([ast.alias("gwfal", "_GWFAL")]),
                # _GWFAL_root = _GWFAL_twr.Resource()
                ast.Assign([ast.Name("_GWFAL_root", ast.Store())],
                           ast.Call(load_attrib("_GWFAL_twr", "Resource"), [], [], None, None)),
                ]

            for child in node.body:
                new_child = self.visit(child)
                if isinstance(new_child, ast.AST):
                    L.append(ast.fix_missing_locations(new_child))
                else:
                    L.extend(ast.fix_missing_locations(s) for s in new_child)

            # _GWFAL._main(port, _GWFAL_root)
            L.append(ast.Expr(
                    ast.Call(load_attrib("_GWFAL", "_main"),
                             [ast.Num(port), load_name("_GWFAL_root")],
                             [], None, None)))
            return ast.Module([ast.fix_missing_locations(a) for a in L])

    transformer = GWFALNodeTransformer()
    new_ast = transformer.visit(AST)
    return new_ast

# Transform the AST.
def _run():
    frame = inspect.currentframe()
    while frame.f_back:
        frame = frame.f_back
    filename = inspect.getabsfile(frame)
    a = ast.parse(open(filename).read())
    new_ast = _transform_ast(a, frame.f_globals.get('PORT', 8080))
    exec compile(new_ast, filename, "exec") in {}
    sys.exit(0)

def _main(port, root):
    print ">>> GWFAL is listening on 0.0.0.0:" + str(port)
    application = service.Application("Generic Web Framework Abstraction Layer")
    internet.TCPServer(port, server.Site(root)).setServiceParent(application)
    app.startApplication(application, False)
    reactor.run()

def respond(value):
    frame_globals = inspect.currentframe(1).f_globals
    frame_globals["_GWFAL_response"] += value

get = post = request = None

__all__ = ['get', 'post', 'respond', 'request']

_run()
