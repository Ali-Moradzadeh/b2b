from threading import Thread, Lock


def do_thread_work(thread_group_id, thread_target, thread_target_args, thread_target_kwargs):
    if ThreadQueue.locking:
        lock = ThreadGroup.get_lock(thread_group_id)
        with lock:
            result = thread_target(*thread_target_args, **thread_target_kwargs)
            ThreadGroup.get_group(thread_group_id)._add_result(result)
    else:
        result = thread_target(*thread_target_args, **thread_target_kwargs)
        ThreadGroup.get_group(thread_group_id)._add_result(result)


class ThreadGroupMultipleTargetException(Exception):
    pass


class ThreadGroup:
    _groups = {}
    
    def __new__(cls, id, target, save_results=True):
        if id not in cls._groups:
            cls._groups[id] = super().__new__(cls)
            cls._groups[id].id = id
            cls._groups[id].threads = []
            cls._groups[id].target = target
            cls._groups[id]._lock = Lock()
            cls._groups[id]._results = []
            cls._groups[id].save_results = save_results
        elif cls._groups[id].target != target:
            raise ThreadGroupMultipleTargetException("Can't set various targets for a ThreadGroup")
        return cls._groups[id]

    
    @classmethod
    def get_lock(cls, id):
        return cls._groups[id]._lock
    
    @classmethod
    def get_group(cls, id):
        return cls._groups[id]
    
    
    def _add_result(self, result):
        if self.save_results:
            self._results.append(result)
    
    def get_results(self):
        return self._results
    
    def _register(self, args=(), kwargs={}):
        t = Thread(target=do_thread_work, args=(self.id, self.target, args, kwargs))
        self.threads.append(t)


class ThreadQueue:
    _instance = None
    locking = True

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._thread_groups = []
    
    @classmethod
    def refresh(cls):
        cls._instance = None
        ThreadGroup._groups = {}
    
    def get_thread_groups(self):
        return self._thread_groups
    
    def establish(self, thread_group, args=(), kwargs={}):
        not_exist = thread_group not in self._thread_groups
        if not_exist:
            self._thread_groups.append(thread_group)
        thread_group._register(args, kwargs)
        return not_exist

    
    def start_join_all(self, max_connection):
        threads = []
        for tg in self._thread_groups:
        	threads.extend(tg.threads)
        
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        """
        i = 0
        while i < len(threads):
            sub = threads[i:i+max_connection]
            i += max_connection
            for thread in sub:
                thread.start()
            for thread in sub:
                thread.join()
        """
