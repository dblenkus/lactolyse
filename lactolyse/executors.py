""".. Ignore pydocstyle D400.

========
Exectuor
========

Executor is the central point which takes care to setup the runtime
environment and run all analyses.

At the moment only Docker executor is implemented:

.. autoclass:: lactolyse.executors.DockerExecutor
    :members:

"""
import atexit
import inspect
import logging
import os
import shutil
import sys
import tempfile
import time
from importlib import import_module

import docker

from lactolyse.analyses.base import BaseAnalysis

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

__all__ = ('executor',)

ANALYSES_PACKAGE = 'lactolyse.analyses'
DOCKER_IMAGE = 'domenblenkus/lactolyse:latest'
DOCKER_START_COMMAND = "/bin/sh -c 'sleep infinity'"
DOCKER_MOUNT_POINT = '/mnt'

docker_client = docker.from_env()  # pylint: disable=invalid-name


def remove_docker_container(container_id):
    """Return the function which removes the Docker container with thhe given id when called."""
    def _remove_container():
        """Remove the Docker container."""
        try:
            container = docker_client.containers.get(container_id)
        except docker.errors.NotFound:
            # Looks like container has already been removed.
            return

        # container.stop()
        container.remove(force=True)

    return _remove_container


class DockerExecutor():
    """Executor using Docker container for the environment.

    This executor starts a Docker container at the initiazlization and
    executes all commands inside it.
    """

    def __init__(self):
        self._runtime_root = tempfile.TemporaryDirectory()
        logger.info("Runtime root: %s", self._runtime_root.name)

        self._container = None
        self._analyses = {}

        self._create_container(ignore_errors=True)
        self._discover_analyses()

    def _create_container(self, ignore_errors=False):
        """Create the container."""
        runtime_mount = docker.types.Mount(DOCKER_MOUNT_POINT, self._runtime_root.name, 'bind')

        logger.debug("Creating container.")
        try:
            self._container = docker_client.containers.run(
                DOCKER_IMAGE, DOCKER_START_COMMAND, mounts=[runtime_mount], detach=True
            )
        except docker.errors.ImageNotFound:
            if ignore_errors:
                logger.warning("Container image not found.")
                return

            logger.exception("Container image not found.")
            raise

        logger.info("Container created: %s", self._container.id)

        # Remove the container on exit.
        atexit.register(remove_docker_container(self._container.id))

    def _validate_analysis(self, analysis):
        """Validate that given analysis has required parameters."""
        cls_name = analysis.__name__

        assert analysis.name, (
            "Subclass '{}' must have defined 'name' attribute.".format(cls_name)
        )
        assert analysis.template, (
            "Subclass '{}' must have defined 'template' attribute.".format(cls_name)
        )

    def _discover_analyses(self):
        """Iterate over files in analyses package and import all found analyses."""
        analyses_package = import_module(ANALYSES_PACKAGE)
        files = next(os.walk(analyses_package.__path__[0]))[2]

        for fn in files:
            fn = fn.rstrip('.py')
            module = import_module('{}.{}'.format(ANALYSES_PACKAGE, fn))

            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                if (not inspect.isclass(attr)
                        or not issubclass(attr, BaseAnalysis)
                        or attr is BaseAnalysis):
                    continue

                self._validate_analysis(attr)
                self._analyses[attr.name] = attr

        logger.info("Found %d analyses: %s", len(self._analyses), list(self._analyses.keys()))

    def _check_container(self):
        """Check that container is up and running.

        Reload the container status and start it if it is not running
        already. If the container doesn't exist anymore, create a new
        one.
        """
        if self._container is None:
            self._create_container()

        try:
            self._container.reload()
        except docker.errors.NotFound:
            logger.warning("Container cannot be found, creating a new one.")
            self._create_container()

            return

        if self._container.status != 'running':
            logger.warning("Container was not running, starting it.")
            self._container.start()

    def get_docker_images(self):
        """Return list of Docker images used by executor."""
        return [DOCKER_IMAGE]

    def run(self, analysis, output_path, inputs=None):
        """Run the analysis."""
        if inputs is None:
            inputs = {}

        if not isinstance(inputs, dict):
            raise ValueError("Attribute 'inputs' must be of type 'dict' or 'None'.")

        if analysis not in self._analyses.keys():
            raise ValueError(
                "Unknown analysis '{}', select one of the following: {}".format(
                    analysis, ", ".join(self._analyses.keys())
                )
            )

        self._check_container()

        with tempfile.TemporaryDirectory(dir=self._runtime_root.name) as runtime_dir:
            analysis = self._analyses[analysis](runtime_dir=runtime_dir)

            start_time = time.time()

            logger.debug("Running run_render_context method.")
            analysis.run_render_context(inputs)

            logger.debug("Running render_template method.")
            analysis.render_template()

            logger.debug("Compiling report.")
            result = self._container.exec_run(
                "/bin/sh -c 'cd {}; {}'".format(
                    os.path.join(DOCKER_MOUNT_POINT, os.path.basename(runtime_dir)),
                    analysis.run_command,
                )
            )

            logger.info("Report finished in {:.2f}s.".format(time.time() - start_time))

            if result.exit_code != 0:
                message = "Something went wrong while rendering report."
                logger.error(message)
                print(result.output)
                raise RuntimeError(message)

            shutil.copy(analysis.get_pdf_file(), output_path)

        return analysis.run_get_results()


executor = None  # pylint: disable=invalid-name
# Initialize executor only in workers.
if sys.argv[1] == 'runworker':
    executor = DockerExecutor()  # pylint: disable=invalid-name
