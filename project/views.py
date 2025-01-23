from django.http import JsonResponse
from .models import Task

def get_tasks_for_project(request):
    project_id = request.GET.get('project')
    if project_id:
        tasks = Task.objects.filter(project_id=project_id).values('id', 'title')
        return JsonResponse(list(tasks), safe=False)
    return JsonResponse([])