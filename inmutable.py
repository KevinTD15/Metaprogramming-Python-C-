import threading


class ImmutableMeta(type):
    # nombres mangleados con __ para simular comportamiento privado
    __attrModdifiers = {} # aqui almacenaremos tuplas de las dos funciones que modifican atributos de una clase
    __lock = threading.Lock() # utilizaremos locks para evitar condiciones de carrera

    def __error_notifier(*args,**kwargs): #nombre mangleado
        raise AttributeError("Attribute Modifications are not allowed")

    def __call__(cls, *args, **kwargs):
        with ImmutableMeta.__lock:
            # guardamos los modificadores de atributos en nuestro diccionario
            if cls not in cls.__attrModdifiers:
                ImmutableMeta.__attrModdifiers[cls] = cls.__setattr__, cls.__delattr__
            else:
                # restauramos los modificadores dummy para que las instanciaciones añadan sus propiedades
                cls.__setattr__,cls.__delattr__ = ImmutableMeta.__attrModdifiers[cls]
            #instanciamos llamando al call de type q llamara al new y al init de la clase
            instance = super(ImmutableMeta, cls).__call__(*args, **kwargs)
            # sustituimos los modifficadores por una funcion dummy que arroje excepcion
            cls.__setattr__ = cls.__delattr__ = ImmutableMeta.__error_notifier
            return instance
