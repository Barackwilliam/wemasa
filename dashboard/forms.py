from django import forms
from django.db import models
from django.forms import inlineformset_factory, modelform_factory
from django.utils.html import escape
from django.utils.safestring import mark_safe

from website.models import GalleryImage, Project, ProjectStat, RichTextField

SKIP_FIELDS = {"id", "created_at", "updated_at"}


class RichTextWidget(forms.Widget):
    """A hidden input edited through the Trix rich-text editor."""

    def render(self, name, value, attrs=None, renderer=None):
        field_id = (attrs or {}).get("id", f"id_{name}")
        return mark_safe(
            f'<input type="hidden" id="{escape(field_id)}" name="{escape(name)}" value="{escape(value or "")}">'
            f'<trix-editor input="{escape(field_id)}" class="trix-content"></trix-editor>'
        )


class ImagePreviewWidget(forms.ClearableFileInput):
    template_name = "dashboard/widgets/image.html"

    def __init__(self, attrs=None):
        super().__init__({"accept": "image/*", **(attrs or {})})


class FilePreviewWidget(forms.ClearableFileInput):
    template_name = "dashboard/widgets/image.html"


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"accept": "image/*", "multiple": True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single = super().clean
        if isinstance(data, (list, tuple)):
            return [single(item, initial) for item in data]
        return [single(data, initial)] if data else []


def widget_for(db_field, **kwargs):
    if isinstance(db_field, RichTextField):
        return db_field.formfield(widget=RichTextWidget, **kwargs)
    if isinstance(db_field, models.ImageField):
        return db_field.formfield(widget=ImagePreviewWidget, **kwargs)
    if isinstance(db_field, models.FileField):
        return db_field.formfield(widget=FilePreviewWidget, **kwargs)
    if isinstance(db_field, models.DateTimeField):
        return db_field.formfield(
            widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"], **kwargs,
        )
    if isinstance(db_field, models.DateField):
        return db_field.formfield(widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"), **kwargs)
    if isinstance(db_field, models.ManyToManyField):
        return db_field.formfield(widget=forms.CheckboxSelectMultiple, **kwargs)
    if isinstance(db_field, models.TextField):
        return db_field.formfield(widget=forms.Textarea(attrs={"rows": 4}), **kwargs)
    return db_field.formfield(**kwargs)


def editable_fields(section):
    names = []
    for f in section.model._meta.get_fields():
        if not getattr(f, "editable", False) or f.auto_created or f.name in SKIP_FIELDS or f.name in section.exclude:
            continue
        if f.is_relation and f.one_to_many:
            continue
        names.append(f.name)
    return names


def form_for(section):
    fields = [f for fs in section.fieldsets for f in fs[1]] if section.fieldsets else editable_fields(section)
    return modelform_factory(section.model, fields=fields, formfield_callback=widget_for)


def fieldsets_for(section, form):
    if section.fieldsets:
        return [(title, [form[name] for name in names]) for title, names in section.fieldsets]
    return [("", [form[name] for name in form.fields])]


INLINE_FORMSETS = {
    "stats": inlineformset_factory(
        Project, ProjectStat, fields=["label", "value", "order"], extra=3, can_delete=True,
        widgets={"order": forms.NumberInput(attrs={"style": "max-width:90px"})},
    ),
}
INLINE_TITLES = {"stats": ("Project facts", "Extra facts shown beside the project, e.g. “Students — About 3,700” or “Schools — Kibasila, Kongowe”.")}


class BulkPhotoForm(forms.Form):
    photos = MultipleImageField(label="Photos", help_text="Select one or many photos at once (JPG, PNG or WebP).")
    project = forms.ModelChoiceField(
        Project.objects.all(), required=False, empty_label="— Not linked to a project —",
        help_text="Linked photos also appear on the project's page.",
    )
    album = forms.CharField(required=False, max_length=80, help_text="Optional album name for the gallery page.")
    caption = forms.CharField(required=False, max_length=250, help_text="Optional caption applied to every photo.")

    def save(self):
        created = []
        for upload in self.cleaned_data["photos"]:
            created.append(GalleryImage.objects.create(
                image=upload,
                project=self.cleaned_data["project"],
                album=self.cleaned_data["album"],
                caption=self.cleaned_data["caption"],
            ))
        return created
