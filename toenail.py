
from genshi.core import QName, TEXT
from genshi.template import MarkupTemplate, directives

class jQueryBuilder(object):
    def __init__(self, initial):
        self.initial = initial
        self.operations = []

    def __getattr__(self, name):
        self.operations.append(("get", name))
        return self

    def __getitem__(self, idx):
        self.operations.append(("get", str(idx)))
        return self

    def __call__(self, *args):
        self.operations.append(("call", args))
        return self

    def __str__(self):
        return self.build()

    def build(self):
        parts = ['jQuery(%r)' % (self.initial,)]
        for op in self.operations:
            optype, args = op
            if optype == "get":
                # args = field name
                if isinstance(args, basestring):
                    parts.append("." + args)
                else:
                    parts.append("[" + self.format_arg(args) + "]")
            elif optype == "call":
                # args = callees
                parts.append("(")
                parts.extend(self.format_arg(a) for a in args)
                parts.append(")")
        return ''.join(parts)

    def format_arg(self, arg):
        if isinstance(arg, unicode):
            arg = arg.encode("utf8")

        if isinstance(arg, str):
            return '"' + arg.replace('"', '\\"') + '"'

        if isinstance(arg, (int, long)):
            return str(arg)

        if isinstance(arg, bool):
            return "true" if arg else "false"

class ServerDirective(directives.Directive):
    js_event = None
    def __call__(self, stream, children, ctxt, **vars):
        templ_global = ctxt.frames[-1]
        event_map = templ_global.setdefault('__toenail_event_map', {})

        def _generate():
            kind, (tag, attrib), pos = stream.next()
            tag_id = attrib.get('id')
            if tag_id is None:
                tag_count = templ_global.setdefault('__toenail_id_counter', 0)
                templ_global['__toenail_id_counter'] += 1

                tag_id = "__toenail_id_%d" % (tag_count,)
                attrib |= [(QName('id'), tag_id)]

            events = event_map.setdefault(tag_id, [])
            events.append((self.js_event, len(events), self.expr.source))

            yield kind, (tag, attrib), pos
            for event in stream:
                yield event

        return directives._apply_directives(_generate(), children, ctxt, vars)

class JSEventDirective(directives.Directive):
    tagname = "jsevents"

    PROLOGUE = """function _toenail_dispatch(e,i){$.ajax("/ajax/toenail_response/"+$(this).attr('id')+"/"+i).done(function(r){$.globalEval(r)})}"""

    def __call__(self, stream, children, ctxt, **vars):
        templ_global = ctxt.frames[-1]
        event_map = templ_global.get('__toenail_event_map', {})

        def _generate():
            kind, (tag, attrib), pos = stream.next()
            attrib |= [(QName('id'), '__toenail_logic_main')]
            yield kind, (tag, attrib), pos

            statements = [self.PROLOGUE]
            for tag_id, jsevents in event_map.iteritems():
                for event_type, event_id, expr in jsevents:
                    js = """$("#%s").bind("%s", _toenail_dispatch, %d)""" % (tag_id, event_type, event_id)
                    statements.append(js)

            js = "$(function(){%s})" % (';'.join(statements),)
            yield TEXT, js, 0

            for event in stream:
                yield event

        return directives._apply_directives(_generate(), children, ctxt, vars)

class ToenailMarkupTemplate(MarkupTemplate):
    def get_directive(self, name):
        if name.lower().startswith("on"):
            event = name[2:].lower()
            tagname = "On"+event.capitalize()
            cls = type(str(tagname+"Directive"), (ServerDirective,), dict(js_event=event))
            cls.tagname = tagname.lower()
            return cls
        if name.lower() == "jsevents":
            return JSEventDirective

        return super(ToenailMarkupTemplate, self).get_directive(name)

if __name__ == "__main__":
    builder = jQueryBuilder('#id').slideDown()
    print builder

    print

    mt = ToenailMarkupTemplate("""
<html xmlns:py="http://genshi.edgewall.org/">
  <h1 py:content="name" py:onmouseover="thing.foo()"></h1>
  <script py:jsevents=""></script>
</html>
    """)

    stream = mt.generate(name="Yo!")
    print stream.render('xhtml')
