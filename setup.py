from setuptools import setup

setup(
    name='simple-template-engine',
    version='0.1',
    description="Template engine created for self-education",
    author="Alexander Smirnov",
    author_email='maintheme11@gmail.com',
    url='https://github.com/smirnoval/simple-template-engine',
    packages=[
        'src',
        'tests',
    ],
    entry_points='''
        [python.templating.engines]
        simple_template_engine = src.main
    ''',
    license="MIT license",
    keywords='simple-template-engine',
    classifiers=[
        'Development Status :: Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
    ],
)
