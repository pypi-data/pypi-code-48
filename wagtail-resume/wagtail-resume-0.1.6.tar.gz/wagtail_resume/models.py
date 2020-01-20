from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core import blocks, fields
from wagtail.core.models import Page
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.models import Image
from wagtailmarkdown.edit_handlers import MarkdownPanel
from wagtailmarkdown.fields import MarkdownField
from wagtailmetadata.models import MetadataMixin

from .blocks import (
    ContributionsBlock,
    EducationBlock,
    WorkExperienceBlock,
    WritingsBlock,
)


class BaseResumePage(MetadataMixin, Page):
    page_ptr = models.OneToOneField(
        Page, parent_link=True, related_name="+", on_delete=models.CASCADE
    )
    is_creatable = False

    font = models.CharField(max_length=100, null=True, blank=True)
    background_color = models.CharField(max_length=100, null=True, blank=True)

    full_name = models.CharField(max_length=100, null=True, blank=True)

    role = models.CharField(max_length=100, null=True, blank=True)
    about = MarkdownField(max_length=2500, null=True, blank=True)
    photo = models.ForeignKey(
        Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    social_links = fields.StreamField(
        [
            (
                "social_link",
                blocks.StructBlock(
                    [
                        ("text", blocks.TextBlock()),
                        ("url", blocks.URLBlock()),
                        ("logo", ImageChooserBlock()),
                    ],
                    icon="group",
                ),
            ),
        ],
        null=True,
        blank=True,
    )

    resume = fields.StreamField(
        [
            ("work_experience", WorkExperienceBlock()),
            ("contributions", ContributionsBlock()),
            ("writing", WritingsBlock()),
            ("education", EducationBlock()),
        ],
        null=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldPanel("font"), FieldPanel("background_color"),],
            heading="Customization",
        ),
        MultiFieldPanel(
            [
                FieldPanel("full_name"),
                FieldPanel("role"),
                MarkdownPanel("about"),
                ImageChooserPanel("photo"),
                StreamFieldPanel("social_links"),
            ],
            heading="Personal details",
        ),
        StreamFieldPanel("resume"),
    ]

    def get_template(self, request):  # pylint: disable=arguments-differ
        return "wagtail_resume/resume_page.html"

    def get_meta_title(self):
        return self.full_name

    def get_meta_description(self):
        return f"{self.full_name} - {self.role}"

    def get_meta_image(self):
        return self.photo

    def get_meta_url(self):
        return self.get_full_url

    def get_meta_twitter_card_type(self):
        return self.photo
