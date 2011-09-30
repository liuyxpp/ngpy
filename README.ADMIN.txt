* start ZEO server
    in the test.fs directory, run
        runzeo -a localhost:1234 -f ./test.fs

* start eye server
    in ~/opt/eye, run
        bin/eye -p 1111 zeo://localhost:1234
    browse it in FireFox with
        http://127.0.0.1:1111

* PUSH source to Bitbucket
    hg push https://liuyxpp@bitbucket.org/liuyxpp/ngpy
