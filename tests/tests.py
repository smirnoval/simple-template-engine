import unittest
from src.base import Template, Collector


class VariableTests(unittest.TestCase):

    def test_one_variable(self):
        rendered = Template('<div>{{name}}</div>').render(name='alex')
        self.assertEqual(rendered, '<div>alex</div>')

    def test_two_variables_in_different_blocks(self):
        rendered = Template('<div>{{first_name}}</div><div>{{second_name}}</div>').render(first_name='alex', second_name='fedor')
        self.assertEqual(rendered, '<div>alex</div><div>fedor</div>')

    def test_two_variables_in_same_block(self):
        rendered = Template('<div>{{first_name}}, {{second_name}}</div>').render(first_name='alex', second_name='fedor')
        self.assertEqual(rendered, '<div>alex, fedor</div>')


class ArrayTests(unittest.TestCase):

    def test_array_iterable_in_context(self):
        rendered = Template('{% array items %}<div>{{item}}</div>{% end %}').render(items=['alex', 'fedor'])
        self.assertEqual(rendered, '<div>alex</div><div>fedor</div>')

    def test_array_iterable(self):
        rendered = Template('{% array [1, 2, 3] %}<div>{{item}}</div>{% end %}').render()
        self.assertEqual(rendered, '<div>1</div><div>2</div><div>3</div>')

    def test_array_parent_context(self):
        rendered = Template('{% array [1, 2, 3] %}<div>{{..name}}-{{item}}</div>{% end %}').render(name='word')
        self.assertEqual(rendered, '<div>word-1</div><div>word-2</div><div>word-3</div>')


class IfTests(unittest.TestCase):

    def test_if_is_true(self):
        rendered = Template('{% if num > 1 %}<div>more than 1</div>{% end %}').render(num=2)
        self.assertEqual(rendered, '<div>more than 1</div>')

    def test_if_is_false(self):
        rendered = Template('{% if num > 1 %}<div>more than 1</div>{% end %}').render(num=0)
        self.assertEqual(rendered, '')

    def test_if_else_if_is_true(self):
        rendered = Template('{% if num > 1 %}<div>more than 1</div>{% else %}<div>less than 1</div>{% end %}').render(num=2)
        self.assertEqual(rendered, '<div>more than 1</div>')

    def test_if_else_if_is_false(self):
        rendered = Template('{% if num > 1 %}<div>more than 1</div>{% else %}<div>less or equal to 1</div>{% end %}').render(num=0)
        self.assertEqual(rendered, '<div>less or equal to 1</div>')


class CollectorTests(unittest.TestCase):

    def test_open_file(self):
        test_file = Collector('single_page.html')
        self.assertEqual(str(test_file), '<div>{{name}}</div>')

    def test_render_opened_file(self):
        test_file = Collector('single_page.html').assemble_page(name='alex')
        self.assertEqual(str(test_file), '<div>alex</div>')

    def test_collect_child_and_parent(self):
        test_file = Collector('basic_inheritance/child.html').assemble_page(name='alex', variable="value")
        test_value = """<!DOCTYPE html>
<html lang="en">
<head>
    <title> alex amazing blog
My amazing blog2 </title>
</head>

<body>
    <div id="sidebar">
        <h1>Sidebar</h1>
    </div>
    <div id="plain_div">
        <h2>Another div with value</h2>
    </div>
    <div id="content">
        <h1>Content</h1>
    </div>
</body>
</html>"""
        self.assertEqual(str(test_file), test_value)

    def test_collect_child_and_parent(self):
        test_file = Collector("few_nested_templates/test3.html").assemble_page()
        test_value = """ amazing blog 

	<h1>Content</h1>
	<h1>Sidebar</h1>

"""
        self.assertEqual(str(test_file), test_value)


if __name__ == '__main__':
    unittest.main()
