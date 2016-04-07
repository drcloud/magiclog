#!/usr/bin/env python

from setuptools import setup


conf = dict(name='magiclog',
            version='1.0.1',
            author='Jason Dusek',
            author_email='jason.dusek@gmail.com',
            url='https://github.com/drcloud/magiclog',
            install_requires=[],
            setup_requires=['pytest-runner', 'setuptools'],
            tests_require=['flake8', 'pytest', 'tox'],
            description='Easy logger management for libraries and CLI tools.',
            py_modules=['magiclog'],
            classifiers=['Environment :: Console',
                         'Intended Audience :: Developers',
                         'Operating System :: Unix',
                         'Operating System :: POSIX',
                         'Programming Language :: Python',
                         'Topic :: Software Development',
                         'Development Status :: 4 - Beta'])


if __name__ == '__main__':
    setup(**conf)
