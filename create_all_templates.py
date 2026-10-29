import os

templates_to_create = {
    'accounts/student_list.html': """{% extends 'base.html' %}
{% block title %}Students{% endblock %}
{% block content %}
<div class="card p-6">
    <h2 class="text-xl font-bold mb-4">Student Management</h2>
    <p class="text-slate-600">Student list view is ready. (Placeholder for full implementation)</p>
    <a href="{% url 'dashboard' %}" class="btn-secondary btn-sm mt-4 inline-block">Back to Dashboard</a>
</div>
{% endblock %}""",

    'accounts/lecturer_list.html': """{% extends 'base.html' %}
{% block title %}Lecturers{% endblock %}
{% block content %}
<div class="card p-6">
    <h2 class="text-xl font-bold mb-4">Lecturer Management</h2>
    <p class="text-slate-600">Lecturer list view is ready. (Placeholder for full implementation)</p>
    <a href="{% url 'dashboard' %}" class="btn-secondary btn-sm mt-4 inline-block">Back to Dashboard</a>
</div>
{% endblock %}""",

    'academics/department_list.html': """{% extends 'base.html' %}
{% block title %}Departments{% endblock %}
{% block content %}
<div class="card p-6">
    <h2 class="text-xl font-bold mb-4">Department Management</h2>
    <p class="text-slate-600">Department list view is ready. (Placeholder for full implementation)</p>
    <a href="{% url 'dashboard' %}" class="btn-secondary btn-sm mt-4 inline-block">Back to Dashboard</a>
</div>
{% endblock %}""",

    'academics/course_list.html': """{% extends 'base.html' %}
{% block title %}Courses{% endblock %}
{% block content %}
<div class="card p-6">
    <h2 class="text-xl font-bold mb-4">Course Management</h2>
    <p class="text-slate-600">Course list view is ready. (Placeholder for full implementation)</p>
    <a href="{% url 'dashboard' %}" class="btn-secondary btn-sm mt-4 inline-block">Back to Dashboard</a>
</div>
{% endblock %}""",

    'academics/enrollment_list.html': """{% extends 'base.html' %}
{% block title %}Enrollments{% endblock %}
{% block content %}
<div class="card p-6">
    <h2 class="text-xl font-bold mb-4">Enrollment Management</h2>
    <p class="text-slate-600">Enrollment list view is ready. (Placeholder for full implementation)</p>
    <a href="{% url 'dashboard' %}" class="btn-secondary btn-sm mt-4 inline-block">Back to Dashboard</a>
</div>
{% endblock %}""",

    'attendance/fingerprint_list.html': """{% extends 'base.html' %}
{% block title %}Fingerprint Profiles{% endblock %}
{% block content %}
<div class="card p-6">
    <h2 class="text-xl font-bold mb-4">Fingerprint Profile Management</h2>
    <p class="text-slate-600">Fingerprint list view is ready. (Placeholder for full implementation)</p>
    <a href="{% url 'dashboard' %}" class="btn-secondary btn-sm mt-4 inline-block">Back to Dashboard</a>
</div>
{% endblock %}""",

    'attendance/session_list.html': """{% extends 'base.html' %}
{% block title %}Attendance Sessions{% endblock %}
{% block content %}
<div class="card p-6">
    <h2 class="text-xl font-bold mb-4">Attendance Sessions</h2>
    <p class="text-slate-600">Session list view is ready. (Placeholder for full implementation)</p>
    <a href="{% url 'dashboard' %}" class="btn-secondary btn-sm mt-4 inline-block">Back to Dashboard</a>
</div>
{% endblock %}""",

    'attendance/scan.html': """{% extends 'base.html' %}
{% block title %}Scan Attendance{% endblock %}
{% block content %}
<div class="card p-6">
    <h2 class="text-xl font-bold mb-4">Demo Fingerprint Scanner</h2>
    <p class="text-slate-600">Scanning interface is ready. (Placeholder for full implementation)</p>
    <a href="{% url 'dashboard' %}" class="btn-secondary btn-sm mt-4 inline-block">Back to Dashboard</a>
</div>
{% endblock %}""",

    'attendance/reports.html': """{% extends 'base.html' %}
{% block title %}Attendance Reports{% endblock %}
{% block content %}
<div class="card p-6">
    <h2 class="text-xl font-bold mb-4">Attendance Reports</h2>
    <p class="text-slate-600">Reports view is ready. (Placeholder for full implementation)</p>
    <a href="{% url 'dashboard' %}" class="btn-secondary btn-sm mt-4 inline-block">Back to Dashboard</a>
</div>
{% endblock %}""",

    'dashboard/lecturer_dashboard.html': """{% extends 'base.html' %}
{% block title %}Lecturer Dashboard{% endblock %}
{% block content %}
<div class="card p-6">
    <h2 class="text-xl font-bold mb-4">Lecturer Dashboard</h2>
    <p class="text-slate-600">Welcome, Lecturer. Your dashboard is ready.</p>
    <form method="post" action="{% url 'logout' %}">
        {% csrf_token %}
        <button type="submit" class="btn-danger btn-sm mt-4">Sign Out</button>
    </form>
</div>
{% endblock %}"""
}

for path, content in templates_to_create.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print('ALL MISSING TEMPLATES CREATED SUCCESSFULLY!')
