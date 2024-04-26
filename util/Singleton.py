
INSTANCES = {}

def singleton(cls):
    """
    Singleton decorator to ensure a class is defined only once
    """

    def get_instance(*args, **kwargs):
        if cls not in INSTANCES:
            INSTANCES[cls] = cls(*args, **kwargs)
        return INSTANCES[cls]

    return get_instance
