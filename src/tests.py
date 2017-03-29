import unittest
from base import Template


class EachTests(unittest.TestCase):

    def test_each_iterable_in_context(self):
        rendered = Template('{% each items %}<div>{{it}}</div>{% end %}').render(items=['alex', 'maria'])
        self.assertEqual(rendered, '<div>alex</div><div>maria</div>')

    def test_each_iterable_as_literal_list(self):
        rendered = Template('{% each [1, 2, 3] %}<div>{{it}}</div>{% end %}').render()
        self.assertEqual(rendered, '<div>1</div><div>2</div><div>3</div>')

    def test_each_parent_context(self):
        rendered = Template('{% each [1, 2, 3] %}<div>{{..name}}-{{it}}</div>{% end %}').render(name='jon doe')
        self.assertEqual(rendered, '<div>jon doe-1</div><div>jon doe-2</div><div>jon doe-3</div>')

    def test_each_space_issues(self):
        rendered = Template('{% each [1,2, 3]%}<div>{{it}}</div>{%end%}').render()
        self.assertEqual(rendered, '<div>1</div><div>2</div><div>3</div>')

    def test_each_no_tags_inside(self):
        rendered = Template('{% each [1,2,3] %}<br>{% end %}').render()
        self.assertEqual(rendered, '<br><br><br>')

    def test_nested_objects(self):
        context = {'lines': [{'name': 'l1'}], 'name': 'p1'}
        rendered = Template('<h1>{{name}}</h1>{% each lines %}<span class="{{..name}}-{{it.name}}">{{it.name}}</span>{% end %}').render(**context)
        self.assertEqual(rendered, '<h1>p1</h1><span class="p1-l1">l1</span>')


if __name__ == '__main__':
    unittest.main()