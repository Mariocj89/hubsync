#!/usr/bin/env python
from setuptools import setup
setup(
  name = 'hubsync',
  packages = ['hubsync'],
  version = '0.1.3',
  description = 'Get your github workspace synced!',
  author = 'Mario Corchero',
  author_email = 'mariocj89@gmail.com',
  url = 'https://github.com/Mariocj89/hubsync',
  keywords = ['github', 'sync', 'workspace'],
  scripts=['hubsync.py'],
  test_suite = 'nose.collector',
  use_2to3=True,
  install_requires=['gitpython', 'requests'],
  test_requires=['mock']
)
