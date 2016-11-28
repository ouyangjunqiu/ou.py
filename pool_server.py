# coding=utf-8
import multiprocessing
import os
import time
import Mysql
import OuTimer

from Daemonize import Daemonize, AppExitException


def worker_proc(q, l):
    """

    :type q: multiprocessing.Manager.Queue
    :type l: multiprocessing.Manager.Lock
    """
    print "111111"

    data = q.get()
    print data
    # print "%s" % (data,)
    # if data is None:
    #    return
    mysql = Mysql.Mysql()

    row = mysql.getOne("select * from cps_shop where nick='妙乐乐官方旗舰店'")

    print row
    # with lock:
    #   fsock = open("log/worker.txt", "a")
    #  fsock.write("worker(%r) " % (row,))
    # fsock.close()


class MainServer(object):
    def __init__(self):

        self._db_connection = Mysql.Mysql()
        self._manager = multiprocessing.Manager()

        self._queue = self._manager.Queue()
        self._lock = self._manager.Lock()

        self._pool = multiprocessing.Pool(8)

        self._timer = OuTimer.Timer(5, MainServer._handle_task, args=(self._queue, self._lock))
        self._timer.start()

        # Use signal handler to throw exception which can be caught
        # by worker process to allow graceful exit.
        Daemonize.signal()

    @staticmethod
    def run():
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
    def _handle_task(q, l):
        """

          :type q: multiprocessing.Manager.Queue
          :type l: multiprocessing.Manager.Lock
        """
        q.put("妙乐乐官方旗舰店")


if __name__ == '__main__':
    #Daemonize.init()

    import sys

    print "main process(%d) start" % os.getpid()

    MainServer.run()
    sys.exit(0)
