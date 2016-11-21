import multiprocessing
import os
import signal
import sys
import time

base_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]


class GracefulExitException(Exception):
    @staticmethod
    def sigterm_handler(signum, frame):
        raise GracefulExitException()

    pass


class GracefulExitEvent(object):
    def __init__(self):
        self.workers = []
        self.exit_event = multiprocessing.Event()

        # Use signal handler to throw exception which can be caught
        # by worker process to allow graceful exit.
        signal.signal(signal.SIGTERM, GracefulExitException.sigterm_handler)
        pass

    def reg_worker(self, wp):
        self.workers.append(wp)
        pass

    def is_stop(self):
        return self.exit_event.is_set()

    def notify_stop(self):
        for wp in self.workers:
            wp.terminate()

        for wp in self.workers:
            wp.join()

    def wait_all(self):
        while True:
            try:

                for wp in self.workers:
                    wp.apply_async(worker_proc, args=())
                time.sleep(0.2)

            except GracefulExitException:
                self.notify_stop()
                print "main process(%d) got GracefulExitException." % os.getpid()
                break
            except Exception, ex:
                self.notify_stop()
                print "main process(%d) got unexpected Exception: %r" % (os.getpid(), ex)
                break
        pass


def worker_proc():

    print "worker(%d) start ..." % os.getpid()


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
    daemonize('/dev/null', log_path + 'trace.log', log_path + 'error.log')

    # signal.signal(signal.SIGTERM, stop)

    import sys

    print "main process(%d) start" % os.getpid()

    gee = GracefulExitEvent()

    pool = multiprocessing.Pool(8)
    #pool.terminate()

    gee.reg_worker(pool)

    gee.wait_all()
    sys.exit(0)
