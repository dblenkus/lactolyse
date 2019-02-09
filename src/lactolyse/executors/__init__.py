""".. Ignore pydocstyle D400.

=========
Exectuors
=========

Executor is the central point which takes care to setup the runtime
environment and run all analyses.

Built-in executors are:

.. autoclass:: lactolyse.executors.docker.Executor
    :members:

.. autoclass:: lactolyse.executors.local.Executor
    :members:

"""
import os
import pkgutil
import sys
from importlib import import_module

# Keep Django as a loose dependency.
try:
    from django.core.exceptions import ImproperlyConfigured as error_class
except ImportError:
    error_class = RuntimeError

DEFAULT_EXECUTOR = 'lactolyse.executors.docker'

__all__ = 'executor'


def load_executor(executor_name):
    """Load executor."""
    try:
        return import_module('{}'.format(executor_name))
    except ImportError as err:
        # The executor wasn't found. Display a helpful error message
        # listing all possible (built-in) executors.
        executors_dir = os.path.dirname(__file__)

        try:
            builtin_executors = [
                name for _, name, _ in pkgutil.iter_modules([executors_dir])
            ]
        except EnvironmentError:
            builtin_executors = []
        if executor_name not in [
            'lactolyse.executors.docker.{}'.format(b) for b in builtin_executors
        ]:
            executor_reprs = map(repr, sorted(builtin_executors))
            error_msg = (
                "{} isn't an available executor.\n"
                "Try using 'lactolyse.executors.docker.XXX', where XXX is one of:\n"
                "    {}\n"
                "Error was: {}".format(executor_name, ", ".join(executor_reprs), err)
            )
            raise error_class(error_msg)
        else:
            # If there's some other error, this must be an error in Django
            raise


# Keep Django as a loose dependency.
try:
    from django.conf import settings

    LACTOLYSE_EXECUTOR = getattr(settings, 'LACTOLYSE_EXECUTOR', DEFAULT_EXECUTOR)
except ImportError:
    # Django's settings should be a single source of truth, so environment
    # variable is used only if Django is not installed.
    LACTOLYSE_EXECUTOR = os.environ.get('LACTOLYSE_EXECUTOR', DEFAULT_EXECUTOR)

executor = None
# Initialize executor only in workers.
if len(sys.argv) > 1 and sys.argv[1] == 'runworker':
    executor = load_executor(LACTOLYSE_EXECUTOR).Executor()
