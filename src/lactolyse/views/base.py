"""Lactolyse base forms."""
from django.http import HttpResponseRedirect
from django.views.generic import FormView


class MultiFormView(FormView):
    """Multiform view."""

    form_classes = {}

    def validate_forms(self, forms):
        """Check if forms are valid."""
        return all([form.is_valid() for form in forms.values()])

    def forms_valid(self, forms):
        """If the form is valid, redirect to the supplied URL."""
        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, forms):
        """If the form is invalid, render the invalid form."""
        return self.render_to_response(self.get_context_data(forms=forms))

    def get_forms_kwargs(self):
        """Return the keyword arguments for instantiating forms."""
        initial = self.get_initial()

        kwargs = {}
        for key in self.form_classes:
            kwargs[key] = {'initial': initial.get(key), 'prefix': self.get_prefix()}
            if self.request.method in ('POST', 'PUT'):
                kwargs[key].update(
                    {'data': self.request.POST, 'files': self.request.FILES}
                )

        return kwargs

    def get_forms(self):
        """Return instances of forms to be used in this view."""
        forms = {}
        form_kwargs = self.get_forms_kwargs()
        for key, form_class in self.form_classes.items():
            forms[key] = form_class(**form_kwargs[key])
        return forms

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        kwargs.setdefault('view', self)

        if 'forms' not in kwargs:
            kwargs['forms'] = self.get_forms()

        if self.extra_context is not None:
            kwargs.update(self.extra_context)

        return kwargs

    def post(self, request, **kwargs):
        """Check the form and return the apropriate response."""
        forms = self.get_forms()

        if self.validate_forms(forms):
            return self.forms_valid(forms)
        else:
            return self.forms_invalid(forms)
