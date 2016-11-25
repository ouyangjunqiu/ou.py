# coding=utf-8
import multiprocessing
import os
import signal
import sys
import time
from RuntimeError import AppExitException
import Mysql
import OuTimer

base_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]


def worker_proc(queue, lock):
    """

    :type queue: multiprocessing.Queue
    :type lock: multiprocessing.Lock
    """
    print "111111"

    #data = queue.get()
    #print "%s" % (data,)
    #if data is None:
    #    return
    mysql = Mysql.Mysql()

    row = mysql.getOne("select * from cps_shop where nick='妙乐乐官方旗舰店'")

    print row
    #with lock:
    #   fsock = open("log/worker.txt", "a")
    #  fsock.write("worker(%r) " % (row,))
    # fsock.close()


class MainServer(object):
    def __init__(self):

        self._db_connection = Mysql.Mysql()

        self._queue = multiprocessing.Queue()
        self._lock = multiprocessing.Lock()

        self._pool = multiprocessing.Pool(8)

        self._timer = OuTimer.Timer(5, MainServer._handle_task, args=(self._queue, self._db_connection))
        self._timer.start()

        # Use signal handler to throw exception which can be caught
        # by worker process to allow graceful exit.
        signal.signal(signal.SIGTERM, AppExitException.sigterm_handler)

    @staticmethod
    def create():
        server = MainServer()
        assert isinstance(server, MainServer)
        server.start()

    def start(self):

        while True:
            try:

                self._pool.apply_async(worker_proc, args=(self._queue, self._lock))

                time.sleep(0.2)

            except AppExitException:

                print "main process(%d) got GracefulExitException." % os.getpid()
                break
            except Exception, ex:
                print "main process(%d) got unexpected Exception: %r" % (os.getpid(), ex)
                break

        self._queue.put(None)
        self._timer.terminate()
        self._pool.terminate()
        self._db_connection.dispose()

    @staticmethod
    def _handle_task(queue, mysql):
        """

          :type queue: multiprocessing.Queue
          :type mysql: Mysql.Mysql
        """
        queue.put("妙乐乐官方旗舰店")


def daemonize(stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
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

    for f in sys.stdout, sys.stderr: f.flush()
    si = open(stdin, 'r')
    so = open(stdout, 'a+')
    se = open(stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())


if __name__ == '__main__':

    log_path = base_dir + '/log/'
    if not os.path.isdir(log_path):
        os.makedirs(log_path)
    run_path = base_dir + '/Run_Log/'
    if not os.path.isdir(run_path):
        os.makedirs(run_path)
    # daemonize('/dev/null', log_path + 'trace.log', log_path + 'error.log')

    import sys

    print "main process(%d) start" % os.getpid()

    MainServer.create()
    sys.exit(0)
