'''
NGPy
~~~~

NGPy is a web application that enable online performing and analyzing Monte-Carlo simulation on nucleation and growth phenomena. It can be also used as a web framework to develop your own web applications. NGPy is built on top of Flask.

Quickstart
``````````

1. Install
----------

::

    $ easy_install ngpy

or

::

    $ tar -xvf ngpy-xxx.tar.gz
    $ cd ngpy-xxx
    $ python setup.py install

* Make sure that the NoSQL database redis is installed in your system.
* Other dependencies like ZODB, WTForm, Numpy, and Matplotlib should be
  taken care by easy_install. If not, try to install them mannually.

2. Start ZODB server
--------------------

::

    $ runzeo -a 0.0.0.0:<ZEOPORT> -f /path/to/your/data.fs

* <ZEOPORT> must be an available port number, e.g. 1234

3. Start redis server
---------------------

::

    $ redis-server [/path/to/redis.conf]

4. Start the task queue daemon
------------------------------

::

    $ simd

5. Start ngpy
-------------

::

    $ run-ngpy

The ngpy website should be now served at http://localhost:5000.
You can visit it use any browser (Chrome, Firefox, IE, etc.) via
http://localhost:5000
if you are a local visitor, or
http://IP.of.NGPy.run:5000
if you visit remotely.

Links
`````

* `Website <http://liuyxpp.bitbucket.org>`_
* `Development version <http://bitbucket.org/liuyxpp/ngpy/>`_

'''
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='ngpy',
    version='0.1',
    license='BSD',
    description='Web application for Monte Carlo simulation on nucleation and growth phenomena',
    author='Yi-Xin Liu',
    author_email='liuyxpp@gmail.com',
    url='https://bitbucket.org/liuyxpp/ngpy',
    packages=['ngpy'],
    scripts=['run-ngpy','simd'],
    include_package_data=True,
    zip_safe=False,
    long_description=__doc__,
    platform='linux',
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

