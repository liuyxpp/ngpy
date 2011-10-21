"""
NGPy
~~~~

NGPy is a web application that enable online performing and analyzing
Monte-Carlo simulation on nucleation and growth phenomena. It can be also used as a web framework to develop your own web applications. NGPy is built on top of Flask.

Quickstart
``````````

1. Install

::
    $ easy_install ngpy

* You should install the NoSQL database redis.
* Other dependencies like ZODB, WTForm, Numpy, and Matplotlib should be
      taken care by easy_install. If not, try to install them mannually.

2. Start ZODB server

::
    $ runzeo -a localhost:<port> -f /path/to/your/data.fs

* <port> should be an available port number, e.g. 1234

3. Start redis server

::
    $ redis-server [/path/to/redis.conf]

4. Start the task queue daemon

::
    $ /path/to/simd.py

5. Start the app

::
    $ /path/to/run-ngpy.py

The ngpy website should be served at http://localhost:5000.
You can visit it use any browser (Chrome, Firefox, IE, etc.) via
    http://localhost:5000 # If you are a local visitor.
or
    http://your.domain.com:5000 # If you visit remotely.

Links
`````

* `website <http://liuyxpp.bitbucket.org>`_
* `development version <http://bitbucket.org/liuyxpp/ngpy/>`_

"""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='NGPy',
    version='0.1',
    description='Web application for Monte Carlo simulation on nucleation and growth phenomena',
    author='Yi-Xin Liu',
    author_email='liuyxpp@gmail.com',
    url='https://bitbucket.org/liuyxpp/ngpy',
    packages=['ngpy'],
    long_description=__doc__,
    install_requires=[
        'Flask-WTF>=0.5.2',
        'Flask-ZODB>=0.1',
        'Flask>=0.8',
        'numpy>=1.6.0',
        'matplotlib>=1.0.1',
        'redis>=2.4.9',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ]
     )

