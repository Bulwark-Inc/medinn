from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def dashboard(request):
    is_admin = request.user.groups.filter(name='admin').exists()
    is_student = request.user.groups.filter(name='tudent').exists()
    context = [
        {'is_student': is_student},
        {'is_admin': is_admin}
    ]
    
    if is_student:
        # User is in the Student group
        return render(request, 'users/student_dashboard.html', context[0])
    if is_admin:
        # User is in the Admin group
        return render(request, 'users/admin_dashboard.html', context[1])
    else:
        return HttpResponseForbidden("You do not have access to this page.")
