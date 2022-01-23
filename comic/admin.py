from django.contrib import admin

from .models import Page, ComicPanel, SecretPanel
import tagulous.admin
# admin.site.register(Panel)

admin.site.site_header = 'Anthrofractal administartion'
admin.site.index_title = 'Anthrofractal admin'
admin.site.site_title = 'Anthrofractal admin'


class PageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'panel_count', )
    search_fields = ('number', 'title', )


# @admin.register(Panel)
class ComicPanelAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'page', 'number_in_page', 'tags', 'is_published', )
    search_fields = ('number', 'title', 'alt', 'tags__name', )
    list_filter = ('page', 'published', )

    # fieldsets = (
    #     (None, {
    #         'fields': ('published', 'title', 'alt', 'tags', 'image', )
    #     }),
    #     ('Advanced options (page and number)', {
    #         'classes': ('collapse', ),
    #         'description': "These fields are set automatically but can be changed if needed",
    #         'fields': ('number', 'page', ),
    #     }),
    # )


class SecretPanelAdmin(admin.ModelAdmin):
    list_display = ('key_phrase', 'published', )
    search_fields = ('key_phrase', )
    list_filter = ('published', )

    fieldsets = (
        (None, {
            'fields': ('published', 'key_phrase', 'image', )
        }),
        ('Webpage glitch text overrides', {
            # 'classes': ('collapse', ),
            'description': 'These fields override glitching text (only glitch \'shadows\' themselves, not main text)',
            'fields': ('archive_text', 'howto_text', 'vote_text', 'donate_text', ),
        }),
    )


admin.site.register(Page, PageAdmin)
admin.site.register(SecretPanel, SecretPanelAdmin)
tagulous.admin.register(ComicPanel, ComicPanelAdmin)
tagulous.admin.register(ComicPanel.tags)

