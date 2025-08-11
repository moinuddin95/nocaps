from setuptools import setup, find_packages

setup(
  name='nocaps',
  version='0.7',
  description='A witty Python code roaster and fixer CLI tool.',
  packages=find_packages(),
  install_requires=[
    'google-generativeai>=0.8.5',
    'rich>=14.0.0',
    'python-dotenv>=1.1.0'
  ],
  entry_points={
    "console_scripts":[
      "nocaps = nocaps:main"
    ]
  }
)