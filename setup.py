from setuptools import setup,find_packages

setup(
    name='parser_notam_package',
    version='0.4.1',
    install_requires = [
        'jsonschema'
    ],
    packages=find_packages(),
    description= """
    A Python package to parse and validate NOTAM messages
    """,
    url='https://github.com/hungthinhnguyen2912/notam_parser',
)