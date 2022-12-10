from functools import wraps
from inspect import signature, Parameter

def Contract(*, require, ensure):
    #'require' y 'ensure' son parámetros de sólo palabras clave (keywordOnly) porque aparecen después de una entrada *
    # comprobar 'require' y 'ensure' sean 'callables'
    if not callable(require):
        raise Exception("'require' must be a callable object")
    if not callable(ensure):
        raise Exception("'ensure' must be a callable object")

    def Decorator(func):
        #utilizamos el functools wraps para preservar las caracteristicas de la funcion envuelta
        @wraps(func)
        def Wrapper(*args, **kwargs):
            funcSig = signature(func)
            reqSig = signature(require)
            #verificamos que los parametros de la funcion 'require' sean compatibles con 'func'
            if not CompatibleParams(reqSig.parameters, funcSig.parameters):
                raise Exception("sig mismatch between 'require' and 'func'")

            # verificamos que los parametros de ensure sean los correctos,
            # lo cual es que solo exista solo un argumento sin default parameter y este no sea keyowrd only
            enSig = signature(ensure)
            withoutDefaults = list(filter(lambda p: p.default == Parameter.empty, enSig.parameters.values()))
            if len(withoutDefaults) != 1 or withoutDefaults[0].kind == Parameter.KEYWORD_ONLY:
                raise Exception("invalid params in 'ensure' params")

            # verificamos las precondiciones
            if not require(*args, **kwargs):
                raise Exception("'require' preconditions not satisfied")

            # ejecutamos la funcion
            result = func(*args, **kwargs)

            # verificamos las postcondiciones
            if not ensure(result):
                raise Exception("'ensure' postconditions not satisfied")

            return result
        return Wrapper
    return Decorator

def CompatibleParams(reqSigParams, funcSigParams):
    # todos los parametros postional only de require deben ser la misma cantidad y si sobraran deben tener default value
    posReq = list(filter(lambda p: p[1].kind == Parameter.POSITIONAL_ONLY, reqSigParams.items()))
    posFunc = list(filter(lambda p: p[1].kind == Parameter.POSITIONAL_ONLY, funcSigParams.items()))
    if len(posFunc) < len(posReq) and not all(map(lambda p: p[1].default != Parameter.empty, posReq[len(posFunc):])):
        return False

    # vamos eliminando de los positional_or_keyword de require y nos debemos quedar con la lista vacia o con def values
    posKw = list(filter(lambda p: p[1].kind == Parameter.POSITIONAL_OR_KEYWORD, reqSigParams.items()))
    # los positionals que sobran en func se tienen que eliminar primero
    posKw = posKw[len(posFunc) - len(posReq) if len(posFunc) - len(posReq) > 0 else 0:]
    # los parametros positional_or_keyword de func tienen que llamarse igual que los de require para en caso
    # que los llamen como keyword garantizar la compatibilidad en el peor caso
    for param in filter(lambda p: p[1].kind == Parameter.POSITIONAL_OR_KEYWORD, funcSigParams.items()):
        item = next(filter(lambda p: p[0] == param[0], posKw))
        if item:
            posKw.remove(item)

    # todos los keyowrd o positional_or_keyword de require deben ser eliminados por kewords de func
    posKw += list(filter(lambda p: p[1].kind == Parameter.KEYWORD_ONLY, reqSigParams.items()))
    for param in filter(lambda p: p[1].kind == Parameter.KEYWORD_ONLY, funcSigParams.items()):
        item = next(filter(lambda p: p[0] == param[0], posKw))
        if item:
            posKw.remove(item)

    # si al final quedase algun parametro keyowrd o positional_or_keyword en require debe tener valor por defecto
    if len(posKw) and not all(map(lambda p: p[1].default != Parameter.empty, posKw)):
        return False

    return True