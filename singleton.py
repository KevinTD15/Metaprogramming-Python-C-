import threading


class SingletonMeta(type):
    # nombres mangleado para simular comportamiento privado
    __iStorage = {} # aqui almacenaremos las instancias,
    __lock = threading.Lock() # un lock para hacer threading safe la instanciacion de singletos (problema comun)

    def __call__(cls, *args, **kwargs):
        with SingletonMeta.__lock:
            if cls not in cls.__iStorage:
                # si no esta en nuestro storage de instancias llamamos al call de type (padre)
                # que es el que llama a new e init de la clase
                SingletonMeta.__iStorage[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls.__iStorage[cls]
