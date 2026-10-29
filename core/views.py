from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Attendance System Deployed Successfully!</h1><p><a href='/admin/'>Go to Admin Login</a></p>")
