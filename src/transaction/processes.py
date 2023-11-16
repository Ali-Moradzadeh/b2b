from random import shuffle
from multiprocessing import Process, Lock, Queue
from django.db import connections


def do_process_work(queue, process_group_id, process_target, process_target_args, process_target_kwargs):
    
    connections.close_all()
    result = process_target(*process_target_args, **process_target_kwargs)
    
    if result:
        pre_results = queue.get()
        ProcessGroup.get_group(process_group_id)._add_result(result)
        pre_results.append(result)
        queue.put(pre_results)


class ProcessGroupMultipleTargetException(Exception):
    pass


class ProcessGroup:
    _groups = {}
    
    def __new__(cls, id, target, django_db_blocker, save_results=True):
        if id not in cls._groups:
            instance = cls._groups[id] = super().__new__(cls)
            instance.id = id
            instance.processes = []
            instance.target = target
            instance._blocker = django_db_blocker
            instance._lock = Lock()
            instance._results = []
            instance.save_results = save_results
            instance.queue = Queue()
            instance.queue.put(instance._results)
        
        elif cls._groups[id].target != target:
            raise ProcessGroupMultipleTargetException("Can't set various targets for a ProcessGroup")
        return cls._groups[id]

    
    @classmethod
    def get_lock(cls, id):
        return cls._groups[id]._lock
    
    @classmethod
    def get_blocker(cls, id):
        return cls._groups[id]._blocker
    
    @classmethod
    def get_group(cls, id):
        return cls._groups[id]
    
    
    def _add_result(self, result):
        if self.save_results:
            self._results.append(result)
    
    def get_results(self):
        results = self.queue.get()
        self.queue.put(results)
        return results
        
    
    def _register(self, args=(), kwargs={}):
        t = Process(target=do_process_work, args=(self.queue, self.id, self.target, args, kwargs))
        self.processes.append(t)


class ProcessQueue:
    _instance = None
    locking = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._process_groups = []
    
    @classmethod
    def refresh(cls):
        cls._instance = None
        ProcessGroup._groups = {}
    
    def get_process_groups(self):
        return self._process_groups
    
    def establish(self, process_group, args=(), kwargs={}):
        not_exist = process_group not in self._process_groups
        if not_exist:
            self._process_groups.append(process_group)
        process_group._register(args, kwargs)
        return not_exist

    
    def start_join_all(self):
        processes = []
        for pg in self._process_groups:
        	processes.extend(pg.processes)
        shuffle(processes)
        
        for process in processes:
            process.start()
        for process in processes:
            process.join()
