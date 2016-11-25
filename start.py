import multiprocessing
import os
import signal
import sys
import time
import RuntimeError

reload(sys)
# sys.setdefaultencoding("UTF-8")
base_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]


class GracefulExitEvent(object):
    def __init__(self):
        self.workers = []
        self.exit_event = multiprocessing.Event()

        # Use signal handler to throw exception which can be caught
        # by worker process to allow graceful exit.
        signal.signal(signal.SIGTERM, RuntimeError.AppExitException.sigterm_handler)
        pass

    def reg_worker(self, wp):
        self.workers.append(wp)
        pass

    def is_stop(self):
        return self.exit_event.is_set()

    def notify_stop(self):
        self.exit_event.set()

    def wait_all(self):
        while True:
            try:
                for wp in self.workers:
                    wp.join()

                print "main process(%d) exit." % os.getpid()
                break
            except RuntimeError.AppExitException:
                self.notify_stop()
                print "main process(%d) got GracefulExitException." % os.getpid()
            except Exception, ex:
                self.notify_stop()
                print "main process(%d) got unexpected Exception: %r" % (os.getpid(), ex)
                break
        pass


def worker_proc(gee):
    import sys, time
    print "worker(%d) start ..." % os.getpid()
    try:
        while not gee.is_stop():
            # do task job here
            print ".",
            gee.wait(1)
        else:
            print ""
            print "worker process(%d) got exit event." % os.getpid()
            print "worker process(%d) do cleanup..." % os.getpid()
            time.sleep(1)
            print "[%d] 3" % os.getpid()
            time.sleep(1)
            print "[%d] 2" % os.getpid()
            time.sleep(1)
            print "[%d] 1" % os.getpid()

    except RuntimeError.AppExitException:
        print "worker(%d) got GracefulExitException" % os.getpid()
    except Exception, ex:
        print "Exception:", ex
    finally:
        print "worker(%d) exit." % os.getpid()
        sys.exit(0)


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

    # signal.signal(signal.SIGTERM, stop)

    import sys

    print "main process(%d) start" % os.getpid()

    gee = GracefulExitEvent()

    # Start some workers process and run forever
    for i in range(0, 10):
        wp = multiprocessing.Process(target=worker_proc, args=(gee,))
        wp.start()
        gee.reg_worker(wp)

    gee.wait_all()
    sys.exit(0)
