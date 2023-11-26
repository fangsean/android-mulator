import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor


class ThreadPool:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=30)

    def get_executor(self):
        return self.executor


pool = ThreadPool()


class EventLoopThreadExecutor(object):

    def create_event_loop_thread(self, func, *args, **kwargs):

        def _worker(*args, **kwargs):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                loop.run_until_complete(func(*args, **kwargs))
            finally:
                loop.close()

        return threading.Thread(target=_worker, args=args, kwargs=kwargs, daemon=True)

    def exetute(self, *threads, wait: bool = False):
        for thread in threads:
            if isinstance(thread, threading.Thread):
                # thread.daemon = True
                thread.start()

        if wait:
            for thread in threads:
                if isinstance(thread, threading.Thread):
                    thread.join()


loop_executor = EventLoopThreadExecutor()


import asyncio
import threading

class ParallelExecutor:

    def create_event_loop_thread(self, func, *args, **kwargs):
        async def worker():
            await func(*args, **kwargs)

        loop = asyncio.new_event_loop()
        t = threading.Thread(target=loop.run_until_complete,
                             args=(worker(),), daemon=True)
        t.start()
        return t

    def execute(self, *tasks, wait=False):
        threads = [self.create_event_loop_thread(task) for task in tasks]
        if wait:
            for thread in threads:
                thread.join()

executor = ParallelExecutor()

