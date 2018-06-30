"""Lactolyse base analysis."""
import os

import jinja2

TEX_JOB_NAME = 'report'

latex_jinja_env = jinja2.Environment(  # pylint: disable=invalid-name
    block_start_string=r'\BLOCK{',
    block_end_string=r'}',
    variable_start_string=r'\VAR{',
    variable_end_string=r'}',
    comment_start_string=r'\#{',
    comment_end_string=r'}',
    line_statement_prefix=r'%%',
    line_comment_prefix=r'%#',
    trim_blocks=True,
    autoescape=False,
    loader=jinja2.PackageLoader('lactolyse', os.path.join('templates', 'lactolyse', 'latex'))
)


class BaseAnalysis:
    """Base class for performing analyses."""

    def __init__(self, runtime_dir):
        """Initialize analysis and set variables based on given runtime dir."""
        self._runtime_dir = runtime_dir

        self._tex_file = os.path.join(self._runtime_dir, TEX_JOB_NAME + '.tex')
        self._pdf_file = os.path.join(self._runtime_dir, TEX_JOB_NAME + '.pdf')

        self._context = None
        self._rendered_template = None

    @property
    def name(self):
        """Name of the analysis."""
        raise NotImplementedError(
            "Subclass od 'BaseAnalysis' must define 'name' attribute."
        )

    @property
    def template(self):
        """Filename of the template file."""
        raise NotImplementedError(
            "Subclass od 'BaseAnalysis' must define 'template' attribute."
        )

    def get_pdf_file(self):
        """Return the path to the PDF file."""
        return self._pdf_file

    def render_context(self, inputs):
        """Calculate context for ``render_template`` method.

        This function should be overriden in subclass.
        """
        return {}

    def run_render_context(self, *args, **kwargs):
        """Run ``render_context`` and save the result.

        This is a utility function that simplify writing of
        ``render_context`` function and remove the need of directly
        accessing ``self._context`` argument.
        """
        self._context = self.render_context(*args, **kwargs)

    @property
    def run_command(self):
        """Command for preparing report."""
        return 'xelatex -interaction=nonstopmode -jobname={0} {0}.tex'.format(TEX_JOB_NAME)

    def render_template(self):
        """Redner template and save it to a file."""
        template = latex_jinja_env.get_template(self.template)
        self._rendered_template = template.render(**self._context)

        with open(self._tex_file, 'w', encoding="utf-8") as fn:
            fn.write(self._rendered_template)

    def get_results(self, context):
        """Return the result of the analysis.

        This function should be overriden in subclass.
        """
        return {}

    def run_get_results(self):
        """Run ``get_results`` and pass the context to it.

        This is a utility function that simplify writing of
        ``get_results`` function and remove the need of directly
        accessing ``self._context`` argument.
        """
        return self.get_results(self._context)
