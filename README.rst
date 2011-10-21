NGPy
~~~~

NGPy is a web application that enable online performing and analyzing Monte-Carlo simulation on nucleation and growth phenomena. It can be also used as a web framework to develop your own web applications. NGPy is built on top of Flask.

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

5. Start ngpy

::

    $ /path/to/run-ngpy.py

    The ngpy website should be served at http://localhost:5000.
    You can visit it use any browser (Chrome, Firefox, IE, etc.) via
        http://localhost:5000
    if you are a local visitor, or
        http://IP.of.NGPy.run:5000 
    if you visit remotely.

Links
`````

* `Website <http://liuyxpp.bitbucket.org>`_
* `Development version <http://bitbucket.org/liuyxpp/ngpy/>`_

