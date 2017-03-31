# simple-template-engine

Simple template engine

https://travis-ci.org/smirnoval/simple-template-engine.svg?branch=master

### Inheritance

base.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="stylesheet" href="style.css" />
    <title>{? title ?} {? endblock ?}</title>
</head>

<body>
    <div id="content">
        {? content ?}

        {? endblock ?}
    </div>
</body>
</html>
```

child.html
```html
{! "base.html" !}

{? title ?} Amazing blog {? endblock ?}

{? content ?}
    <h1>Content</h1>
{? endblock ?}
```

result
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="stylesheet" href="style.css" />
    <title> Amazing blog </title>
</head>

<body>
    <div id="content">
    <h1>Content</h1>
    </div>
</body>
</html>
```


### Variables

```html
<h1>{{variable}}</h1>
```

### Loops

Example:

```python
items = [1, 2, 3]
```

```html
{% array items %}<div>{{item}}</div>{% end %}'
```

result
```html
<div>1</div><div>2</div><div>3</div>
```

### Conditional statement

Supported operators are: `>, >=, <, <=, ==, !=`.

```html
{% if num > 5 %}
    <div>more</div>
{% else %}
    <div>less or equal</div>
{% end %}

{% if items %}
    <div>we have items</div>
{% end %}
```