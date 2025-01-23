from django.contrib import admin
from .models import Task, Project, Comment, File, TimeSheet
from django import forms
from django.db.models import Q
from django.urls import path
from django.http import JsonResponse

from datetime import date





class MasterAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        # Set the created_user only for new instances
        if not obj.pk:
            obj.created_user = request.user
        super().save_model(request, obj, form, change)

from django.contrib.auth.models import Group, User

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'min': date.today().isoformat(),  # Restrict past dates
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'min': date.today().isoformat(),
            }),
        }
    

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        # Ensure start_date is not later than end_date
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date cannot be later than end date.")

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Group users by their roles
        grouped_users = []
        groups = Group.objects.exclude(name='Project Manager')

        for group in groups:
            # Get users in this group
            users_in_group = User.objects.filter(groups=group).order_by('username')
            if users_in_group.exists():
                # Add group and its users as a tuple
                grouped_users.append((group.name, [(user.id, user.username) for user in users_in_group]))

        # Set the grouped choices for the `team` field
        self.fields['team'].queryset = User.objects.all()
        self.fields['team'].widget = forms.SelectMultiple()
        self.fields['team'].choices = grouped_users
        

from django.urls import reverse
from django.utils.html import format_html

class ProjectAdmin(MasterAdmin):
    
    list_display = ('name', 'status', 'start_date', 'end_date', 'priority', 'task_count', 'view_tasks_link')

    def view_tasks_link(self, obj):
        """Generates a link to view tasks of the project."""
        url = reverse('admin:project_task_changelist')  # Replace 'app_name' with your app's name
        return format_html('<a href="{}?project__id__exact={}">View Tasks</a>', url, obj.id)

    view_tasks_link.short_description = 'Tasks'

    def task_count(self, obj):
        """Show the task count based on user role."""
        user = self.request.user

        # If superuser, show total task count
        if user.is_superuser:
            return obj.task_set.count()

        # For Team Managers and Team Leads
        if user.groups.filter(name__in=["Project Manager", "Project Lead"]).exists():
            return obj.task_set.count()
        

        # For Developers, show only tasks assigned to them
        return obj.task_set.filter(assigned_to=user).count()

    task_count.short_description = 'Task Count'

    # Include filter_horizontal and form configurations
    form = ProjectForm
    readonly_fields = ('created_user',)
    filter_horizontal = ('team',)

    def get_queryset(self, request):
        self.request = request  # Save request to use in `task_count`
        queryset = super().get_queryset(request)

        # Filter projects where the logged-in user is part of the team or the creator
        if not request.user.is_superuser:
            queryset = queryset.filter(Q(team=request.user) | Q(created_user=request.user)).distinct()

        return queryset

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        # If the user is a Project Lead, make specific fields read-only except for 'status'
        if request.user.groups.filter(name="Project Lead").exists():
            readonly_fields += ('is_active', 'name', 'description', 'start_date', 'end_date', 'priority', 'team')

        return readonly_fields
    

#-----------------------Task Section----------------------------------
class FileInline(admin.TabularInline):
    readonly_fields = ('created_user',)
    model = File
    extra = 1


class TaskAdminForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'

        widgets = {
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'min': date.today().isoformat(),  # Restrict past dates
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'min': date.today().isoformat(),
            }),
        }
    

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        due_date = cleaned_data.get('due_date')
        project = cleaned_data.get('project')  # Fetch the selected project

        if start_date and project.start_date and start_date < project.start_date:
            raise forms.ValidationError(f"Task start date cannot be earlier than the project's start date ({project.start_date}).")

        if due_date and project.end_date and due_date > project.end_date:
            raise forms.ValidationError(f"Task due date cannot be later than the project's end date ({project.end_date}).")

        # Ensure start_date is not later than due_date
        if start_date and due_date and start_date > due_date:
            raise forms.ValidationError("Start date cannot be later than due date.")

        return cleaned_data


from django.db.models import Case, When, Value, IntegerField

class TaskAdmin(MasterAdmin):
    change_form_template = "admin/project/task/change_form.html"
    form = TaskAdminForm
    
    
    readonly_fields = ('created_user','due_date')
    inlines = [FileInline]
    list_display = ('project', 'title', 'status', 'priority')


    def save_related(self, request, form, formsets, change):
        # Attach the request object to each inline instance
        for formset in formsets:
            for obj in formset.save(commit=False):
                if isinstance(obj, File):
                    obj._request = request
        super().save_related(request, form, formsets, change)
    

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('fetch-team-members/', self.fetch_team_members, name='fetch-team-members'),
        ]
        return custom_urls + urls

    def fetch_team_members(self, request):
        project_id = request.GET.get('project_id')
        if not project_id:
            return JsonResponse({'error': 'No project ID provided'}, status=400)

        try:
            project = Project.objects.get(id=project_id)
            team_members = project.team.all().values('id', 'username')
            return JsonResponse({'team_members': list(team_members)})
        except Project.DoesNotExist:
            return JsonResponse({'error': 'Project not found'}, status=404)
    

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        # Define a custom order for the status field
        status_order = {
            'New': 1,
            'Reopened': 2,
            'Inprogress': 3,
            'Resolved': 4,
            'Closed': 5,
        }

        # If user is not superuser, filter tasks
        if not request.user.is_superuser:
            # If user is a developer, show only their assigned tasks
            if request.user.groups.filter(name="developer").exists():
                queryset = queryset.filter(assigned_to=request.user)
            else:
                # For other roles (Project Lead, etc.), show tasks where they're in the project team
                queryset = queryset.filter(
                    Q(project__team=request.user) | Q(created_user=request.user)
                ).distinct()

        # Add a custom ordering based on status
        queryset = queryset.annotate(
            status_order=Case(
                *[When(status=status, then=Value(order)) for status, order in status_order.items()],
                default=Value(999),
                output_field=IntegerField()
            )
        ).order_by('status_order')

        return queryset
    
    # def get_readonly_fields(self, request, obj=None):
    #     readonly_fields = super().get_readonly_fields(request, obj)
        
    #     # If the user is a developer, make the fields read-only except for 'status'
    #     if request.user.groups.filter(name="developers").exists():
    #         readonly_fields += ('is_active', 'title', 'description', 'project', 'assigned_to', 'tracker_type', 'severity', 'reproducibility', 'steps_to_reproduce', 'environment', 'start_date', 'due_date', 'priority')
        
    #     # If the user is a tester, make these fields read-only
    #     elif request.user.groups.filter(name="tester").exists():
    #         readonly_fields += ('is_active', 'title', 'description', 'project', 'assigned_to', 'severity', 'reproducibility', 'steps_to_reproduce', 'environment', 'start_date', 'due_date', 'priority')
        
    #     return readonly_fields
    
    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     """
    #     Filter the 'project' and 'assigned_to' fields based on the Team Lead's team.
    #     """
    #     if db_field.name == "project":
    #         if request.user.groups.filter(name="Project Lead").exists():
    #             # Show only projects where the Team Lead is a part of the team
    #             kwargs['queryset'] = Project.objects.filter(team=request.user)

        
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

#----------------------Comment Section--------------------------    

class CommentAdmin(MasterAdmin):
    readonly_fields = ('created_user',)
    list_display = ('task','created_user')
    fields = ('title','task','content','is_active')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Filter projects where the logged-in user is in the team
        if not request.user.is_superuser:  # Allow superusers to see all projects
            queryset = queryset.filter(Q(task__assigned_to=request.user) | Q(created_user=request.user))

        # Check if the user is a Team Lead and filter tasks with comments visible for them
        if request.user.groups.filter(name="Project Lead").exists():
            # Get tasks where the user is in the project's team
            queryset = queryset.filter(task__project__team=request.user)

            # Prefetch related comments for these tasks
            queryset = queryset.prefetch_related('task__comment')

        return queryset
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filter the 'project' and 'assigned_to' fields based on the Team Lead's team.
        """
        if db_field.name == "task":
            if request.user.groups.filter(name="Testers").exists():
                # Show only projects where the Team Lead is a part of the team
                kwargs['queryset'] = Task.objects.filter(status='Resolved', project__team=request.user)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    
#-------------------------File Section-------------------------------

class FileAdmin(MasterAdmin):
    readonly_fields = ('created_user',)
    list_display = ('task','name', 'file')
    fields = ('task', 'name', 'file')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Filter projects where the logged-in user is in the team
        if not request.user.is_superuser:  # Allow superusers to see all projects
            queryset = queryset.filter(Q(task__assigned_to=request.user) | Q(created_user=request.user))
        return queryset

    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_user for new objects
            obj.created_user = request.user
        super().save_model(request, obj, form, change)


class TimeSheetAdmin(MasterAdmin):
    exclude = ('created_user',)
    list_display = ('task','project','created_user','date')
#Register models to admin panel

admin.site.register(Task,TaskAdmin)
admin.site.register(Project,ProjectAdmin)
admin.site.register(Comment,CommentAdmin)
admin.site.register(File,FileAdmin)
admin.site.register(TimeSheet,TimeSheetAdmin)