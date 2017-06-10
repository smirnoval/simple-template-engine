# simple-template-engine

Simple template engine

![alt tag](https://travis-ci.org/smirnoval/simple-template-engine.svg?branch=master)


### Straight inheritance

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


### "Include" inheritance

base.html
```html
<!DOCTYPE html>
<html>
{# header.html #}
<body>
  <h1>Welcome!</h1>
</body>
{# footer.html #}
</html>
```

header.html
```html
<head>
    <meta charset="utf-8">
    <title>Title of site</title>
</head>
```

footer.html
```html
<footer>
   <p><strong>Just example of footer</strong></p>
</footer>
```

result
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Title of site</title>
</head>
<body>
  <h1>Welcome!</h1>
</body>
<footer>
   <p><strong>Just example of footer</strong></p>
</footer>
</html>
```


### Combined inheritance

base.html
```html
{! "index.html" !}
{? title ?}<h1>Amazing blog</h1>{? endblock ?}
{? content ?}<h1>Content</h1>{? endblock ?}
```

index.html
```html
<!DOCTYPE html>
<html>
{# header.html #}
{? title ?}{? endblock ?}
<body>
    <h1>Welcome!</h1>
    {? content ?}{? endblock ?}
</body>
{# footer.html #}
</html>
```

header.html
```html
<head>
    <meta charset="utf-8">
    <title>Title of site</title>
</head>
```

footer.html
```html
<footer>
   <p><strong>Just example of footer</strong></p>
</footer>
```

result
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Title of site</title>
</head>
<h1>Amazing blog</h1>
<body>
    <h1>Welcome!</h1>
    <h1>Content</h1>
</body>
<footer>
   <p><strong>Just example of footer</strong></p>
</footer>
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