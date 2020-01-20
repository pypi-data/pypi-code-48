import contextlib

if hasattr(contextlib, 'nullcontext'):
    nullcontext = contextlib.nullcontext
else:
    class nullcontext:
        def __init__(self, enter_result=None):
            self.enter_result = enter_result
        def __enter__(self):
            return self.enter_result
        def __exit__(self, *excinfo):
            pass
