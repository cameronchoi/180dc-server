
from django import template
from django.contrib.admin.templatetags.admin_list import result_list as admin_list_result_list
from django.utils.safestring import mark_safe
from django.contrib.admin.templatetags.base import InclusionAdminNode

def result_list(cl):
    prev = admin_list_result_list(cl)
    prev["result_headers"].append({'text': 'Toggle', 'sortable': False, 'sorted': False, 'ascending': False, 'sort_priority': 0, 'class_attrib': ' class="column-toggle"'})
    options = prev["cl"].queryset.all()
    for i in range(len(options)):
        target_url = f"{options[i].name}"
        prev["results"][i].append(mark_safe(f'<td class="field-toggle"><a href="toggle/{target_url}">Toggle</a></td>'))
    return prev

register = template.Library()

@register.tag(name='result_list')
def result_list_tag(parser, token):
    return InclusionAdminNode(
        parser, token,
        func=result_list,
        template_name='change_list_results.html',
        takes_context=False,
    )