# coding=utf-8
import os
import signal
import sys


class AppExitException(Exception):
    @staticmethod
    def sigterm_handler(signum, frame):
        raise AppExitException()

    pass


class Daemonize:
    def __init__(self):
        Daemonize.init()
        pass

    @staticmethod
    def init():
        base_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
        log_path = base_dir + '/log/'
        if not os.path.isdir(log_path):
            os.makedirs(log_path)
        Daemonize.demon('/dev/null', log_path + 'trace.log', log_path + 'error.log')

    @staticmethod
    def demon(stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
            sys.exit(1)

        os.chdir("/")
        os.umask(0)
        os.setsid()

        for f in sys.stdout, sys.stderr:
            f.flush()
        si = open(stdin, 'r')
        so = open(stdout, 'a+')
        se = open(stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

    @staticmethod
    def signal():
        signal.signal(signal.SIGTERM, AppExitException.sigterm_handler)

