from django.shortcuts import redirect

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.path.startswith('/admin-dashboard/') and not request.user.groups.filter(name='Admin').exists():
                return redirect('student_dashboard')
            if request.path.startswith('/student-dashboard/') and not request.user.groups.filter(name='Student').exists():
                return redirect('admin_dashboard')

        return self.get_response(request)
