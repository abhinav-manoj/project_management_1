from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Master(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name='Active')
    created_user = models.ForeignKey(User, null=True,blank=True, on_delete=models.CASCADE,related_name="%(class)s_created")
    
    class Meta:
        abstract = True
        ordering = ['is_active']


PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]



class Project(Master):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('Inprogress', 'Inprogress'),
        ('Completed', 'Completed'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True,null=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=50, default='New')
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default='Low')
    team = models.ManyToManyField(User,blank=True)

    def __str__(self):
        return self.name


class Task(Master):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('Inprogress', 'Inprogress'),
        ('Resolved', 'Resolved'),
        ('Reopened', 'Reopened'),
        ('closed', 'closed')

    ]
    TRACKER_CHOICES = [
        ('Task', 'Task'),
        ('Bug', 'Bug'),
        ('Feature request', 'Feature request'),
        ('Improvement', 'Improvement')

    ]
    SEVERITY_CHOICES = [
        ('Critical','Critical'),
        ('Major','Major'),
        ('Minor','Minor'),
        ('Trivial','Trivial')
    ]

    REPRODUCTIBILITY_CHOICES = [
        ('Always','Always'),
        ('Sometime','Sometime'),
        ('Rarely','Rarely'),
        ('Unable to Reproduce','Unable to Reproduce'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE,blank=True)
    priority = models.CharField(choices=PRIORITY_CHOICES, max_length=50,default='Low')
    status = models.CharField(choices=STATUS_CHOICES, max_length=50,default='New')
    tracker_type = models.CharField(choices=TRACKER_CHOICES, max_length=50, default='Task')
    severity = models.CharField(choices=SEVERITY_CHOICES, max_length=50, default='Critical')
    reproducibility = models.CharField(choices=REPRODUCTIBILITY_CHOICES, max_length=50, default='Always')
    start_date = models.DateField()
    due_date = models.DateField(blank=True,null=True)
    steps_to_reproduce = models.TextField(blank=True)
    environment = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Comment(Master):
    title = models.CharField(max_length=200, null=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comment')
    content = models.TextField()

    def __str__(self):
        return self.title if self.title else "No Title"


class File(Master):
    name = models.CharField(max_length=50)
    file = models.FileField(upload_to='media/files', max_length=200)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name
    


class TimeSheet(Master):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    
    
    date = models.DateTimeField(auto_now_add=True)
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()

 