import os

import jinja2

TEX_JOB_NAME = 'report'

latex_jinja_env = jinja2.Environment(
    block_start_string='\BLOCK{',
    block_end_string='}',
    variable_start_string='\VAR{',
    variable_end_string='}',
    comment_start_string='\#{',
    comment_end_string='}',
    line_statement_prefix='%%',
    line_comment_prefix='%#',
    trim_blocks=True,
    autoescape=False,
    loader=jinja2.PackageLoader('lactolyse', os.path.join('templates', 'lactolyse', 'latex'))
)


class BaseAnalysis:

    def __init__(self, runtime_dir):
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

        This is a utiliti function that simplify writing of
        ``render_context`` function and remove the need of directly
        accessing ``self._context`` argument.
        """
        self._context = self.render_context(*args, **kwargs)

    @property
    def run_command(self):
        return 'xelatex -interaction=nonstopmode -jobname={0} {0}.tex'.format(TEX_JOB_NAME)

    def render_template(self):
        template = latex_jinja_env.get_template(self.template)
        self._rendered_template = template.render(**self._context)

        with open(self._tex_file, 'w', encoding="utf-8") as fn:
            fn.write(self._rendered_template)
