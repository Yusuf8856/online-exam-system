from django.contrib import admin, messages
from .models import Result

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score', 'total_marks', 'get_percentage', 'date_taken', 'is_published')
    list_filter = ('is_published', 'exam', 'date_taken')
    search_fields = ('student__username', 'exam__name')
    readonly_fields = ('date_taken',)
    actions = ['make_published', 'make_unpublished']

    @admin.action(description="Mark selected results as published")
    def make_published(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"Successfully marked {updated} results as published.", messages.SUCCESS)

    @admin.action(description="Mark selected results as unpublished")
    def make_unpublished(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"Successfully marked {updated} results as unpublished.", messages.WARNING)

    def get_percentage(self, obj):
        if obj.total_marks > 0:
            return f"{(obj.score / obj.total_marks) * 100:.2f}%"
        return "0%"
    
    get_percentage.short_description = 'Percentage'
