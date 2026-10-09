from django import template

register = template.Library()

WIDE_WIDGETS = {"RichTextWidget", "Textarea", "ImagePreviewWidget", "FilePreviewWidget", "CheckboxSelectMultiple"}


@register.filter
def widget_name(bound_field):
    return bound_field.field.widget.__class__.__name__


@register.filter
def is_wide(bound_field):
    return widget_name(bound_field) in WIDE_WIDGETS
