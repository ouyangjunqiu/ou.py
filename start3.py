import multiprocessing
import os
import signal
import sys
import threading
import time
import OuTimer
from RuntimeError import AppExitException

base_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]


class GracefulExitEvent(object):
    def __init__(self):
        self.workers = []
        self.exit_event = multiprocessing.Event()

        # Use signal handler to throw exception which can be caught
        # by worker process to allow graceful exit.
        signal.signal(signal.SIGTERM, AppExitException.sigterm_handler)
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
                time.sleep(1)

            except AppExitException:
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


def _handle_task():
    # reg.apply_async(worker_proc, args=())
    print "main thread running.."


if __name__ == '__main__':

    log_path = base_dir + '/log/'
    if not os.path.isdir(log_path):
        os.makedirs(log_path)
    run_path = base_dir + '/Run_Log/'
    if not os.path.isdir(run_path):
        os.makedirs(run_path)
        # daemonize('/dev/null', log_path + 'trace.log', log_path + 'error.log')

    # signal.signal(signal.SIGTERM, stop)

    import sys

    print "main process(%d) start" % os.getpid()


    # pool = multiprocessing.Pool(8)

    # timer = threading.Timer(1000, _handle_task, (pool,))
    # timer.run()

    thread = OuTimer.Timer(5, _handle_task, args=())
    thread.start()

    signal.signal(signal.SIGTERM, AppExitException.sigterm_handler)

    print "main process(%d) loop" % os.getpid()

    while True:
        try:

            print "main process(%d) running." % (os.getpid())
            time.sleep(0.2)

        except AppExitException:
            # if thread.isAlive():
            #     exit_event.set()
            # else:
            #     print "thread not alive"
            #     os.kill(os.getpid(), signal.SIGTERM)
            thread.terminate()
            print "main process(%d) got GracefulExitException." % (os.getpid())
            break
        except Exception, ex:
            # if thread.isAlive():
            #     exit_event.set()
            # else:
            #     os.kill(os.getpid(), signal.SIGTERM)
            thread.terminate()
            print "main process(%d) got unexpected Exception: %r" % (os.getpid(), ex)
            break

    sys.exit(0)
