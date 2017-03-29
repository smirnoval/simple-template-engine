import re
import logging
import ast


VARIABLE_TOKEN_START = '{{'
VARIABLE_TOKEN_END = '}}'
BLOCK_TOKEN_START = '{%'
BLOCK_TOKEN_END = '%}'

TOKEN_REGEX = re.compile(r"(%s.*?%s|%s.*?%s)" % (
    VARIABLE_TOKEN_START,
    VARIABLE_TOKEN_END,
    BLOCK_TOKEN_START,
    BLOCK_TOKEN_END
))

VARIABLE_FRAGMENT = 0
OPEN_BLOCK_FRAGMENT = 1
CLOSE_BLOCK_FRAGMENT = 2
TEXT_FRAGMENT = 3

WHITESPACE = re.compile('\s+')


class TemplateError(Exception):

    def __init__(self):
        logging.warning('Template error!')


class TemplateContextError(TemplateError):

    def __init__(self, context):
        super().__init__()
        self.context = context
        logging.warning('Template context error!')

    def __str__(self):
        return 'Cannot resolve {0}'.format(self.context_var)


class TemplateSyntaxError(TemplateError):

    def __init(self, syntax_error):
        super().__init__()
        self.syntax_error = syntax_error
        logging.warning('Template syntax error!')

    def __str__(self):
        return 'Invalid syntax {0}'.format(self.syntax_error)


def eval_expression(expr):
    try:
        return 'literal', ast.literal_eval(expr)
    except (ValueError, SyntaxError):
        return 'name', expr


def resolve(name, context):
    if name.startswith('..'):
        context = context.get('..', {})
        name = name[2:]
    try:
        for tok in name.split('.'):
            context = context[tok]
        return context
    except KeyError:
        raise TemplateContextError(name)


class _Fragment(object):
    def __init__(self, raw_text):
        self.raw = raw_text
        self.clean = self.clean_fragment()

    def clean_fragment(self):
        if self.raw[:2] in (VARIABLE_TOKEN_START, BLOCK_TOKEN_START):
            return self.raw[2:-2].strip()
        return self.raw

    @property
    def type(self):
        raw_start = self.raw[:2]
        if raw_start == VARIABLE_TOKEN_START:
            return VARIABLE_FRAGMENT
        elif raw_start == BLOCK_TOKEN_START:
            return CLOSE_BLOCK_FRAGMENT if self.clean[:3] == 'end' else OPEN_BLOCK_FRAGMENT
        else:
            return TEXT_FRAGMENT


class _Node(object):
    creates_scope = False

    def __init__(self, fragment=None):
        self.children = []
        self.process_fragment(fragment)

    def process_fragment(self, fragment):
        pass

    def enter_scope(self):
        pass

    def render(self, context):
        pass

    def exit_scope(self):
        pass

    def render_children(self, context, children=None):
        if children is None:
            children = self.children

        def render_child(child):
            child_html = child.render(context)
            return '' if not child_html else str(child_html)
        return ''.join(map(render_child, children))


class _ScopableNode(_Node):
    creates_scope = True


class _Root(_Node):
    def render(self, context):
        return self.render_children(context)


class _Variable(_Node):
    def process_fragment(self, fragment):
        self.name = fragment

    def render(self, context):
        return resolve(self.name, context)


class _Each(_ScopableNode):
    def process_fragment(self, fragment):
        try:
            _, it = WHITESPACE.split(fragment, 1)
            self.it = eval_expression(it)
        except ValueError:
            raise TemplateSyntaxError(fragment)

    def render(self, context):
        items = self.it[1] if self.it[0] == 'literal' else resolve(self.it[1], context)

        def render_item(item):
            return self.render_children({'..': context, 'it': item})
        return ''.join(map(render_item, items))


class _Text(_Node):
    def process_fragment(self, fragment):
        self.text = fragment

    def render(self, context):
        return self.text


class Compiler(object):

    def __init__(self, template_string):
        self.template_string = template_string

    def each_fragment(self):
        for fragment in TOKEN_REGEX.split(self.template_string):
            if fragment:
                yield _Fragment(fragment)

    def compile(self):
        root = _Root()
        scope_stack = [root]
        for fragment in self.each_fragment():
            if not scope_stack:
                raise TemplateError('nesting issues')
            parent_scope = scope_stack[-1]
            if fragment.type == CLOSE_BLOCK_FRAGMENT:
                parent_scope.exit_scope()
                scope_stack.pop()
                continue
            new_node = self.create_node(fragment)
            if new_node:
                parent_scope.children.append(new_node)
                if new_node.creates_scope:
                    scope_stack.append(new_node)
                    new_node.enter_scope()
        return root

    def create_node(self, fragment):
        node_class = None
        if fragment.type == TEXT_FRAGMENT:
            node_class = _Text
        elif fragment.type == VARIABLE_FRAGMENT:
            node_class = _Variable
        elif fragment.type == OPEN_BLOCK_FRAGMENT:
            cmd = fragment.clean.split()[0]
            if cmd == 'each':
                node_class = _Each
        if node_class is None:
            raise TemplateSyntaxError(fragment)
        return node_class(fragment.clean)


class Template(object):

    def __init__(self, contents):
        self.contents = contents
        self.root = Compiler(contents).compile()

    def render(self, **kwargs):
        return self.root.render(kwargs)