#!/usr/bin/env python

from setuptools import setup


conf = dict(name='magiclog',
            version='0.99.3',
            author='Jason Dusek',
            author_email='jason.dusek@gmail.com',
            url='https://github.com/drcloud/magiclog',
            install_requires=['stackclimber'],
            setup_requires=['pytest-runner', 'setuptools'],
            tests_require=['flake8', 'pytest', 'tox'],
            description='Easy logger management for libraries and CLI tools.',
            py_modules=['magiclog'],
            classifiers=['Environment :: Console',
                         'Intended Audience :: Developers',
                         'License :: OSI Approved :: MIT License',
                         'Operating System :: Unix',
                         'Operating System :: POSIX',
                         'Programming Language :: Python',
                         'Programming Language :: Python :: 2.6',
                         'Programming Language :: Python :: 2.7',
                         'Programming Language :: Python :: 3.5',
                         'Topic :: Software Development',
                         'Development Status :: 4 - Beta'])


if __name__ == '__main__':
    setup(**conf)
