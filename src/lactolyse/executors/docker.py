import atexit
import logging
import os
import shutil
import tempfile
import time

import docker

from lactolyse.registry import registry

logger = logging.getLogger(__name__)

DOCKER_IMAGE = 'domenblenkus/lactolyse:latest'
DOCKER_START_COMMAND = "/bin/sh -c 'sleep infinity'"
DOCKER_MOUNT_POINT = '/mnt'

docker_client = docker.from_env()


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


class Executor:
    """Executor using Docker container for the environment.

    This executor starts a Docker container at the initiazlization and
    executes all commands inside it.
    """

    def __init__(self):
        self._runtime_root = tempfile.TemporaryDirectory()
        logger.info("Runtime root: %s", self._runtime_root.name)

        self._container = None

        self._create_container(ignore_errors=True)

    def _create_container(self, ignore_errors=False):
        """Create the container."""
        runtime_mount = docker.types.Mount(
            DOCKER_MOUNT_POINT, self._runtime_root.name, 'bind'
        )

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

    @classmethod
    def get_docker_images(self):
        """Return list of Docker images used by executor."""
        return [DOCKER_IMAGE]

    def run(self, analysis, output_path, inputs=None):
        """Run the analysis."""
        if inputs is None:
            inputs = {}

        if not isinstance(inputs, dict):
            raise ValueError("Attribute 'inputs' must be of type 'dict' or 'None'.")

        self._check_container()

        with tempfile.TemporaryDirectory(dir=self._runtime_root.name) as runtime_dir:
            analysis = registry.get(analysis)(runtime_dir=runtime_dir)

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
                logger.debug("Output was:\n{}".format(result.output))
                raise RuntimeError(message)

            shutil.copy(analysis.get_pdf_file(), output_path)

        return analysis.run_get_results()
