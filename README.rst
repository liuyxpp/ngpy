NGPy
~~~~

NGPy is a web application that enable online performing and analyzing Monte-Carlo simulations on nucleation and growth phenomena. 
It can be also used as a web framework to develop your own web applications.
NGPy is built on top of **Flask**.
NGPy is actually a distributed system since we use **ZEO server** as a database and **redis** server as a message queue.

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

* Make sure that the NoSQL database **redis** is installed in your system.

* Other dependencies such as **ZODB3**, **WTForm**, **Numpy**, and **Matplotlib** should be taken care by *easy_install*. 
  If not, try to install them mannually.

2. Start ZEO server
--------------------

::

    $ runzeo -a 0.0.0.0:<ZEOPORT> -f /path/to/your/Data.fs

* <ZEOPORT> must be an available port number, e.g. 1234

* The **ZEO** server should run at a host that other hosts can connect to. 

3. Start redis server
---------------------

::

    $ redis-server [/path/to/redis.conf]

* The **redis** server should run at a host that other hosts can connect to.

4. Start the task queue daemon
------------------------------

::

    $ simd [-r <server>] [-q <qkey>]

* <server> is the host where you run the **redis** server.
* What **simd** does is that it just picks the messages from **redis** server and process them.
  So you can run **simd** at every hosts where you wish to run the task.

5. Start ngpy
-------------

::

    $ run-ngpy [-c </path/to/ngpy.cfg>]

The *ngpy.cfg* is the configuration file for **ngpy**. 
It is a Python file and will be processed by **Flask**.
Only values in uppercase are actually used.
More details are refered to the **Flask** documentation.

The **ngpy** website should be now served at http://localhost:5000.
You can visit it use any browser (Chrome, Firefox, IE, etc.) via
http://localhost:5000
if you are a local visitor, or
http://IP.of.NGPy.run:5000 
if you visit remotely.

Ask for Help
````````````

* You can directly contact me at liuyxpp@gmail.com.

* You can join the mailinglist by sending an email to ngpy@librelist.com and replying to the confirmation mail. 
  To unsubscribe, send a mail to ngpy-unsubscribe@librelist.com and reply to the confirmation mail.

Links
`````

* `Website <https://liuyxpp.bitbucket.org>`_

* `Development version <https://bitbucket.org/liuyxpp/ngpy/>`_

* `Dr. Yi-Xin Liu's website <http://ngpy.org>`_
