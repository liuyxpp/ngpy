* start ZEO server
    in the test.fs directory, run
        >runzeo -a localhost:1234 -f ./test.fs

* Pack ZODB database
    >zeopack localhost:1234
    >rm -f test.fs.old

* start eye server
    in ~/opt/eye, run
        >bin/eye -p 1111 zeo://localhost:1234
    browse it in FireFox with
        http://127.0.0.1:1111

* PUSH source to Bitbucket
    >hg push https://liuyxpp@bitbucket.org/liuyxpp/ngpy

* Run Redis server
    >redis-server [/path/to/redis.conf]

* Run the app using the flask server
    >./ngmc.py

* Run the app through apache + mod_wsgi
    >apache start
  and configure the ngmc.wsgi file

* Browse the app in any Browser
via flask server
    http://localhost:5000
    http://10.22.4.52:5000
via apache + mod_wsgi
    http://localhost:8080
    http://10.22.4.52:8080/ngmc

