from random import random
import threading
import time

progress = 0
result = None
result_available = threading.Event()


def background_calculation():
    # here goes some long calculation
    global progress
    for i in range(100):
        time.sleep(random() * 3)
        progress = i + 1

    # when the calculation is done, the result is stored in a global variable
    global result
    result = 42
    result_available.set()

    # do some more work before exiting the thread
    time.sleep(10)


class C:
    def calc(self):
        global progress
        for i in range(100):
            time.sleep(0.1)
            progress += 1
        global result
        result = 50
        result_available.set()


def main():
    c = C()
    # thread = threading.Thread(target=background_calculation)
    thread = threading.Thread(target=c.calc)
    thread.start()

    # wait here for the result to be available before continuing
    while not result_available.wait(timeout=5):
        print('\r{}% done...'.format(progress), end='', flush=True)
    print('\r{}% done...'.format(progress))

    print('The result is', result)


if __name__ == '__main__':
    main()
