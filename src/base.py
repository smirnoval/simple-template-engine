import re
import operator
import ast
import logging


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

OPERATOR_TABLE = {
    '<': operator.lt,
    '>': operator.gt,
    '==': operator.eq,
    '!=': operator.ne,
    '<=': operator.le,
    '>=': operator.ge
}


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


class Fragment:
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


class Node:
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


class Root(Node):
    def render(self, context):
        return self.render_children(context)


class Variable(Node):
    def process_fragment(self, fragment):
        self.name = fragment

    def render(self, context):
        return resolve(self.name, context)


class Array(Node):
    creates_scope = True

    def process_fragment(self, fragment):
        try:
            _, item = WHITESPACE.split(fragment, 1)
            self.item = eval_expression(item)
        except ValueError:
            raise TemplateSyntaxError(fragment)

    def render(self, context):
        items = self.item[1] if self.item[0] == 'literal' else resolve(self.item[1], context)

        def render_item(item):
            return self.render_children({'..': context, 'item': item})
        return ''.join(map(render_item, items))


class If(Node):
    creates_scope = True

    def process_fragment(self, fragment):
        bits = fragment.split()[1:]
        if len(bits) not in (1, 3):
            raise TemplateSyntaxError(fragment)
        self.lhs = eval_expression(bits[0])
        if len(bits) == 3:
            self.op = bits[1]
            self.rhs = eval_expression(bits[2])

    def render(self, context):
        lhs = self.resolve_side(self.lhs, context)
        if hasattr(self, 'op'):
            op = OPERATOR_TABLE.get(self.op)
            if op is None:
                raise TemplateSyntaxError(self.op)
            rhs = self.resolve_side(self.rhs, context)
            exec_if_branch = op(lhs, rhs)
        else:
            exec_if_branch = operator.truth(lhs)
        if_branch, else_branch = self.split_children()
        return self.render_children(context, self.if_branch if exec_if_branch else self.else_branch)

    def resolve_side(self, side, context):
        return side[1] if side[0] == 'literal' else resolve(side[1], context)

    def exit_scope(self):
        self.if_branch, self.else_branch = self.split_children()

    def split_children(self):
        if_branch, else_branch = [], []
        curr = if_branch
        for child in self.children:
            if isinstance(child, Else):
                curr = else_branch
                continue
            curr.append(child)
        return if_branch, else_branch


class Else(Node):
    def render(self, context):
        pass


class Text(Node):
    def process_fragment(self, fragment):
        self.text = fragment

    def render(self, context):
        return self.text


class Compiler:

    def __init__(self, template_string):
        self.template_string = template_string

    def each_fragment(self):
        for fragment in TOKEN_REGEX.split(self.template_string):
            if fragment:
                yield Fragment(fragment)

    def compile(self):
        root = Root()
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
            node_class = Text
        elif fragment.type == VARIABLE_FRAGMENT:
            node_class = Variable
        elif fragment.type == OPEN_BLOCK_FRAGMENT:
            cmd = fragment.clean.split()[0]
            if cmd == 'array':
                node_class = Array
            elif cmd == 'if':
                node_class = If
            elif cmd == 'else':
                node_class = Else
        if node_class is None:
            raise TemplateSyntaxError(fragment)
        return node_class(fragment.clean)


class Template:

    def __init__(self, contents):
        self.contents = contents
        self.root = Compiler(contents).compile()

    def render(self, **kwargs):
        return self.root.render(kwargs)


PAGE_TOKEN_START = '{!'
PAGE_TOKEN_END = '!}'
PAGE_BLOCK_START = '{?'
PAGE_BLOCK_END = '?}'
PAGE_REGEX = re.compile(r"(%s.*?%s)" % (
    PAGE_TOKEN_START,
    PAGE_TOKEN_END
))

PAGE_BLOCKS_REGEX = re.compile(r"({\?.*?\?})")


class Collector:

    def __init__(self, pagename):
        self.pagename = pagename
        with open(self.pagename, 'r') as file:
            self.file = str(file.read())

    def __str__(self):
        return self.file

    def make_page(self, **kwargs):
        components = [x.strip() for x in PAGE_REGEX.split(str(self.file)) if x]
        parent_address = components[0][2:-2].strip().strip('"').strip("'")
        blocks = [x for x in PAGE_BLOCKS_REGEX.split(components[1]) if x != '\n' and x != '']
        dic = {}
        cur = 'temp'
        for i in blocks:
            if i[:2] == '{?' and 'endblock' not in i:
                cur = i[2:-2].strip()
                dic[cur] = []
            elif i[:2] == '{?' and 'endblock' in i:
                cur = 'temp'
            else:
                dic[cur].append(i)
        parent = self.find_parent(parent_address)
        parent = self.find_blocks_for_substition(parent, dic)
        parent = Template(str(parent)).render(**kwargs)
        return parent

    def find_parent(self, parent_name):
        with open(parent_name, 'r') as file:
            return str(file.read())

    def find_blocks_for_substition(self, file, subs):
        components = [x for x in PAGE_BLOCKS_REGEX.split(str(file)) if x]
        dic = {}
        cur = 'temp'
        for i in range(len(components)):
            if components[i][:2] == '{?' and 'endblock' not in components[i]:
                cur = components[i][2:-2].strip()
                dic[cur] = i
                components[i] = ''
            elif components[i][:2] == '{?' and 'endblock' in components[i]:
                components[i] = ''
                cur = 'temp'
            elif cur != 'temp':
                components[i] = ''
        for i in subs.keys():
            if i in dic.keys():
                components[dic[i]] = "".join(subs[i])
        return "".join(components)
