from django.shortcuts import render

def home(request):
    """Render the landing page."""
    return render(request, 'main\home.html')
