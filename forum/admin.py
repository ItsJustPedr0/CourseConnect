from django.contrib import admin
from .models import Department, Course, Prof, Post, Comment, Report

# Department Admin
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbrev', 'slug')
    search_fields = ('name', 'abbrev')
    prepopulated_fields = {'slug': ('abbrev',)}

# Prof Admin
@admin.register(Prof)
class ProfAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'dept', 'slug')
    search_fields = ('first_name', 'last_name')
    list_filter = ('dept',)

# Course Admin
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'dept', 'slug')
    search_fields = ('code', 'name')
    list_filter = ('dept',)
    filter_horizontal = ('prof',)
    prepopulated_fields = {'slug': ('code',)}

# Comment Admin
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at', 'body_preview')
    search_fields = ('post__title', 'body')
    list_filter = ('created_at',)
    readonly_fields = ('post', 'user', 'created_at')
    
    def body_preview(self, obj):
        return obj.body[:50] + '...' if len(obj.body) > 50 else obj.body
    body_preview.short_description = 'Comment'

# Report Admin (Inline)
class ReportInline(admin.TabularInline):
    model = Report
    extra = 0
    readonly_fields = ('user', 'report_type', 'explanation', 'created_at')
    can_delete = False
    fields = ('user', 'report_type', 'explanation', 'created_at')

# Post Admin with inline reports
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'prof', 'post_date', 'report_count')
    search_fields = ('title', 'body')
    list_filter = ('post_date', 'course', 'prof')
    readonly_fields = ('post_date',)
    inlines = [ReportInline]
    actions = ['delete_selected_posts']
    
    def report_count(self, obj):
        count = obj.reports.count()
        if count > 0:
            return f'⚠️ {count} report(s)'
        return 'No reports'
    report_count.short_description = 'Reports'
    
    def delete_selected_posts(self, request, queryset):
        """Custom action to delete selected posts with confirmation"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'Successfully deleted {count} post(s) and associated comments/reports.')
    delete_selected_posts.short_description = '🗑️ Delete selected posts'

# Report Admin (Standalone view for filtering)
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'post_title', 'user', 'report_type', 'created_at', 'status')
    search_fields = ('post__title', 'explanation')
    list_filter = ('report_type', 'created_at', 'post')
    readonly_fields = ('user', 'post', 'explanation', 'created_at')
    fields = ('post', 'user', 'report_type', 'explanation', 'created_at')
    
    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = 'Post Title'
    
    def status(self, obj):
        return '🔴 Unreviewed'
    status.short_description = 'Status'
