"""Lactolyse utils."""
import json
from base64 import b64decode, b64encode
from importlib import import_module


def serialize_model_instance(instance):
    """Generate a base64 encoded reference to a given Django ORM instance."""
    ref = [instance.__class__.__module__, instance.__class__.__name__, instance.pk]
    dumped_ref = json.dumps(ref).encode('utf-8')
    return b64encode(dumped_ref).decode('utf-8')


def deserialize_model_instance(encoded):
    """Load Django ORM instance from base64 encoded reference."""
    dumped_ref = b64decode(encoded)
    ref = json.loads(dumped_ref.decode('utf-8'))

    model_module = import_module(ref[0])
    model_class = getattr(model_module, ref[1])
    return model_class.objects.get(pk=ref[2])
