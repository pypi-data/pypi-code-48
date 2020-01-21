def add(a,b, method = 'i'):

    if a.__class__.__name__ == 'Pbox' or b.__class__.__name__ == 'Pbox':
        return a.add(b, method = method)
    else:
        return a+b

def sub(a,b, method = 'i'):

    if a.__class__.__name__ == 'Pbox' or b.__class__.__name__ == 'Pbox':
        return a.sub(b, method = method)
    else:
        return a-b

def mul(a,b, method = 'i'):

    if a.__class__.__name__ == 'Pbox' or b.__class__.__name__ == 'Pbox':
        return a.mul(b, method = method)
    else:
        return a*b

def div(a,b, method = 'i'):

    if a.__class__.__name__ == 'Pbox' or b.__class__.__name__ == 'Pbox':
        return a.div(b, method = method)
    else:
        return a/b

__all__ = ['add','sub','mul','div']
