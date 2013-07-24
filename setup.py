#!/usr/bin/env python

from setuptools import setup
import vlctvstation

setup(name='VlcTVStation',
      version=vlctvstation.__version__,
      description='Wanna build a tv station in your village? But pay nothing for software, which costs huge money, and nobody cares you have only 5 viewers, well, welcome to vlctvstation then.',
      author='Maxim Nikitenko',
      author_email='sets88@mail.ru',
      packages=['vlctvstation'],
      install_requires=[
          'Flask', 'apscheduler',
      ],
      include_package_data=True,
      zip_safe=False,
      entry_points={
          'console_scripts':
              ['vlctvstation = vlctvstation.vlctvstation:main'],
        }
     )
