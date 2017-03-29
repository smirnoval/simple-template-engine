import unittest
from base import Template


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
        rendered = Template('{% array items %}<div>{{it}}</div>{% end %}').render(items=['alex', 'fedor'])
        self.assertEqual(rendered, '<div>alex</div><div>fedor</div>')

    def test_array_iterable_as_literal_list(self):
        rendered = Template('{% array [1, 2, 3] %}<div>{{it}}</div>{% end %}').render()
        self.assertEqual(rendered, '<div>1</div><div>2</div><div>3</div>')

    def test_array_parent_context(self):
        rendered = Template('{% array [1, 2, 3] %}<div>{{..name}}-{{it}}</div>{% end %}').render(name='jon doe')
        self.assertEqual(rendered, '<div>jon doe-1</div><div>jon doe-2</div><div>jon doe-3</div>')

    def test_array_space_issues(self):
        rendered = Template('{% array [1,2, 3]%}<div>{{it}}</div>{%end%}').render()
        self.assertEqual(rendered, '<div>1</div><div>2</div><div>3</div>')

    def test_array_no_tags_inside(self):
        rendered = Template('{% array [1,2,3] %}<br>{% end %}').render()
        self.assertEqual(rendered, '<br><br><br>')

    def test_nested_objects(self):
        context = {'lines': [{'name': 'l1'}], 'name': 'p1'}
        rendered = Template('<h1>{{name}}</h1>{% array lines %}<span class="{{..name}}-{{it.name}}">{{it.name}}</span>{% end %}').render(**context)
        self.assertEqual(rendered, '<h1>p1</h1><span class="p1-l1">l1</span>')

if __name__ == '__main__':
    unittest.main()
