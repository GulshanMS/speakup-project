from django.contrib import admin
from .models import VoteTopic, Choice, Vote, AnonymousMessage

# Inline for Choice in VoteTopicAdmin
class ChoiceInline(admin.TabularInline):  # or use StackedInline if preferred
    model = Choice
    extra = 2  # shows 2 blank choices by default

# Admin for VoteTopic
@admin.register(VoteTopic)
class VoteTopicAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_active', 'deadline', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('question',)
    ordering = ('-created_at',)
    actions = ['make_active', 'make_inactive']
    fields = ('question', 'description')
    inlines = [ChoiceInline]  # Add this to include choices inline

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Mark selected topics as active"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Mark selected topics as inactive"

# Admin for Vote
@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('topic', 'choice', 'timestamp')  # customize as needed
    list_filter = ('topic',)
    search_fields = ('topic__question',)

# Admin for AnonymousMessage
@admin.register(AnonymousMessage)
class AnonymousMessageAdmin(admin.ModelAdmin):
    list_display = ('content', 'created_at')
    search_fields = ('content',)
