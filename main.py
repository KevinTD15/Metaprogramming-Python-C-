import time
from contract import *
from inspect import signature, Parameter
from singleton import *
from inmutable import *

@Contract(require=lambda x: x > 0, ensure=lambda result=1: result > 0)
def some_function(x):
    pass

def EnsureVerifier(func):
    def wrapper(*args, **kwargs):
        sig = signature(func)
        withoutDefaults = list(filter(lambda p: p.default == Parameter.empty, sig.parameters.values()))
        if len(withoutDefaults) != 1 or withoutDefaults[0].kind == Parameter.KEYWORD_ONLY:
            print ("Invalid ensure params " + func.__name__)
        return 'OK'
    return wrapper

@EnsureVerifier
def f0(x): # Bien
    return True
@EnsureVerifier
def f1(x, y): # Mal
    return True
@EnsureVerifier
def f2(x, y=0): # Bien
    return True
@EnsureVerifier
def f3(x, *, y): # Mal
    return True
@EnsureVerifier
def f4(x, *, y=0): # Bien
    return True
@EnsureVerifier
def f5(x, y, *, z): # Mal
    return True
@EnsureVerifier
def f6(x, y, *, z=0): # Mal
    return True
@EnsureVerifier
def f7(x, y=0, *, z): # Mal
    return True
@EnsureVerifier
def f8(x, y=0, *, z=0): # Bien
    return True


print('EJERCICIO 1')

print(f0(1)) # OK
print(f1(1)) # Invalid ensure params f1
print(f2(1)) # OK
print(f3(1)) # Invalid ensure params f3
print(f4(1)) # OK
print(f5(1)) # Invalid ensure params f5
print(f6(1)) # Invalid ensure params f6
print(f7(1)) # Invalid ensure params f7
print(f8(1)) # OK
#some_function(-1) como x < 0 esto lanza excepci'on


class Inmmutable(metaclass=InmutableMeta):
    def __init__(self):
        self.attr1 = 1

i1 = Inmmutable()

print('\nEJERCICIO 2')

try:
    del i1.attr1 # error al eliminar
except AttributeError:
    print("Error On delete attr1")
try:
    i1.attr2 = 2 # errror al crear
except AttributeError:
    print("Error On create attr2")


print('\nEJERCICIO 3')
class Singleton(metaclass=SingletonMeta):
    def __init__(self):
        self.unique = time.time() # timestamp actual, si se instanciaran dos clases serian distintos en ms
        time.sleep(3)

s1= Singleton()
s2 = Singleton()
print(f'{s1.unique == s2.unique}') # True
