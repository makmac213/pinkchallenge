
from django.utils.safestring import mark_safe

def get_form_error_messages(form):

    errors = '<ul class="errorLists">'

    for field in form:

        if field.errors:
            errors += '<li>'
            errors += '<ul>'

            for error in field.errors:
                errors += '<li>' + error + '</li>'
                
            errors += '</ul>'
            errors += '</li>'

    errors += '</ul>'

    errors += form.non_field_errors().as_ul()

    return mark_safe(errors)
