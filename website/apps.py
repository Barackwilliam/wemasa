from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "website"
    verbose_name = "Website content"

    def ready(self):
        from django.db.models.signals import m2m_changed, post_delete, post_save

        from .cache import bump_content_version

        skip = {"ContactMessage", "Subscriber"}
        for model in self.get_models():
            if model.__name__ in skip:
                continue
            uid = f"wemasa-cache-{model.__name__}"
            post_save.connect(bump_content_version, sender=model, dispatch_uid=f"{uid}-save")
            post_delete.connect(bump_content_version, sender=model, dispatch_uid=f"{uid}-delete")
        m2m_changed.connect(bump_content_version, dispatch_uid="wemasa-cache-m2m")
