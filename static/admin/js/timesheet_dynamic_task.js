django.jQuery(document).ready(function() {
    var projectSelect = django.jQuery('#id_project');
    var taskSelect = django.jQuery('#id_task');

    // Function to update tasks based on selected project
    function updateTasks() {
        var projectId = projectSelect.val();
        if (projectId) {
            // Clear current options
            taskSelect.empty();
            
            // Add loading option
            taskSelect.append(new Option('Loading...', ''));
            
            // Fetch tasks for selected project
            django.jQuery.get('/admin/project/task/', {
                project: projectId
            }).done(function(data) {
                taskSelect.empty();
                taskSelect.append(new Option('---------', ''));
                
                // Add tasks from response
                data.forEach(function(task) {
                    taskSelect.append(new Option(task.title, task.id));
                });
            });
        } else {
            // If no project selected, clear and disable task field
            taskSelect.empty();
            taskSelect.append(new Option('---------', ''));
        }
    }

    // Update tasks when project selection changes
    projectSelect.change(updateTasks);
    
    // Initial update if project is pre-selected
    if (projectSelect.val()) {
        updateTasks();
    }
});