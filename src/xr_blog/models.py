from django.db import models
from django.utils.translation import ugettext as _
from wagtail.admin.edit_handlers import StreamFieldPanel, FieldPanel
from wagtail.core.fields import StreamField

from wagtail.core.models import Page

from xr_pages.blocks import ContentBlock
from xr_pages.models import XrPage


class BlogEntryPage(XrPage):
    template = "xr_blog/pages/blog_entry.html"
    group = models.OneToOneField(
        "xr_pages.LocalGroup", editable=False, on_delete=models.PROTECT
    )
    date = models.DateField(_("Post date"))
    author = models.CharField(max_length=200)
    content = StreamField(
        ContentBlock,
        blank=True,
        help_text=_("The content is only visible on the detail page."),
    )

    # Panels (Editor interface)
    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("author"),
        StreamFieldPanel("content"),
    ]

    parent_page_types = ["BlogListPage"]

    class Meta:
        verbose_name = _("Blog Entry Page")
        verbose_name_plural = _("Blog Entry Pages")

    def save(self, *args, **kwargs):
        if not hasattr(self, "group") or not self.group:
            self.group = self.get_parent().specific.group

        super().save(*args, **kwargs)


class BlogListPage(XrPage):
    template = "xr_blog/pages/blog_list.html"
    group = models.OneToOneField(
        "xr_pages.LocalGroup", editable=False, on_delete=models.PROTECT
    )
    content = StreamField(
        ContentBlock,
        blank=True,
        help_text=_("The content is only visible on the detail page."),
    )

    parent_page_types = ["xr_pages.HomePage", "xr_pages.LocalGroupPage"]

    content_panels = Page.content_panels + [StreamFieldPanel("content")]

    class Meta:
        verbose_name = _("Blog List Page")
        verbose_name_plural = _("Blog List Pages")

    def save(self, *args, **kwargs):
        if not hasattr(self, "group") or not self.group:
            self.group = self.get_parent().specific.group

        super().save(*args, **kwargs)

    def entries(self):
        return BlogEntryPage.objects.child_of(self).live().order_by("-date")
