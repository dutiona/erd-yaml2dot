from setuptools import setup, find_packages

setup(
    name='erd-yaml2dot',
    version='0.1.0',
    description='Generate DOT diagrams from YAML files using Python and Graphviz',
    author='Michaël Roynard',
    author_email='michaelroynard@gmail.com',
    packages=find_packages(),
    install_requires=[
        'graphviz',
        'pyyaml'
    ],
    entry_points={
        'console_scripts': [
            'erd-yaml2dot=erd-yaml2dot.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
