try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(name='nitrile',
      version='0.1',
      author='matt harrison',
      description='utilities to create LaTex',
      modules=['nitrile'],
)
