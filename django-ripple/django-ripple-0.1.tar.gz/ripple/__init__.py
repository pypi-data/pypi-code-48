import importlib

from django.conf import settings

# Not currently used, example for later if needed
def get_signup_serializer():
    import_string = getattr(settings, 'SIGNUP_SERIALIZER')
    if import_string is None:
        import_string = 'ripple.serializers.SignUpSerializer'

    module_path, class_name = import_string.rsplit('.', 1)

    module = importlib.import_module(module_path)
    return getattr(module, class_name)
