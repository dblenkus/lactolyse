import logging
import shutil
import subprocess
import tempfile
import time

from lactolyse.registry import registry

logger = logging.getLogger(__name__)


class Executor:
    """Executor using local environment."""

    def run(self, analysis, output_path, inputs=None):
        """Run the analysis."""
        if inputs is None:
            inputs = {}

        if not isinstance(inputs, dict):
            raise ValueError("Attribute 'inputs' must be of type 'dict' or 'None'.")

        with tempfile.TemporaryDirectory() as runtime_dir:
            analysis = registry.get(analysis)(runtime_dir=runtime_dir)

            start_time = time.time()

            logger.debug("Running run_render_context method.")
            analysis.run_render_context(inputs)

            logger.debug("Running render_template method.")
            analysis.render_template()

            logger.debug("Compiling report.")
            result = subprocess.run(
                analysis.run_command, cwd=runtime_dir, shell=True, capture_output=True
            )

            logger.info("Report finished in {:.2f}s.".format(time.time() - start_time))

            if result.returncode != 0:
                message = "Something went wrong while rendering report."
                logger.error(message)
                logger.debug("Stdout was:\n{}".format(result.stdout))
                logger.debug("Stderr was:\n{}".format(result.stderr))
                raise RuntimeError(message)

            shutil.copy(analysis.get_pdf_file(), output_path)

        return analysis.run_get_results()
