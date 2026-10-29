import os

# 1. Update Department List with Add Button
dept_list = """{% extends 'base.html' %}
{% block title %}Departments{% endblock %}
{% block content %}
<div class="card p-6">
    <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-bold">Department Management</h2>
        <a href="{% url 'department_create' %}" class="btn-primary btn-sm">+ Add Department</a>
    </div>
    <div class="overflow-x-auto">
        <table class="w-full text-sm text-left">
            <thead class="text-xs uppercase bg-slate-50 text-slate-500">
                <tr><th class="px-4 py-3">Code</th><th class="px-4 py-3">Name</th><th class="px-4 py-3">Actions</th></tr>
            </thead>
            <tbody>
                {% for dept in departments %}
                <tr class="border-b bg-white">
                    <td class="px-4 py-3 font-medium">{{ dept.code }}</td>
                    <td class="px-4 py-3">{{ dept.name }}</td>
                    <td class="px-4 py-3">
                        <a href="{% url 'department_update' dept.pk %}" class="text-indigo-600 hover:underline mr-3">Edit</a>
                    </td>
                </tr>
                {% empty %}
                <tr><td colspan="3" class="px-4 py-3 text-center text-slate-500">No departments found. Add one above.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}"""

# 2. Create Department Form
dept_form = """{% extends 'base.html' %}
{% block title %}Add Department{% endblock %}
{% block content %}
<div class="card p-6 max-w-lg mx-auto">
    <h2 class="text-xl font-bold mb-6">Add New Department</h2>
    <form method="post" class="space-y-4">
        {% csrf_token %}
        {{ form.as_p }}
        <div class="flex gap-3 pt-4">
            <button type="submit" class="btn-primary">Save Department</button>
            <a href="{% url 'department_list' %}" class="btn-secondary">Cancel</a>
        </div>
    </form>
</div>
{% endblock %}"""

# 3. Update Student List with Add Button
student_list = """{% extends 'base.html' %}
{% block title %}Students{% endblock %}
{% block content %}
<div class="card p-6">
    <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-bold">Student Management</h2>
        <a href="{% url 'student_create' %}" class="btn-primary btn-sm">+ Add Student</a>
    </div>
    <div class="overflow-x-auto">
        <table class="w-full text-sm text-left">
            <thead class="text-xs uppercase bg-slate-50 text-slate-500">
                <tr><th class="px-4 py-3">Reg Number</th><th class="px-4 py-3">Name</th><th class="px-4 py-3">Department</th><th class="px-4 py-3">Actions</th></tr>
            </thead>
            <tbody>
                {% for student in students %}
                <tr class="border-b bg-white">
                    <td class="px-4 py-3 font-medium">{{ student.registration_number }}</td>
                    <td class="px-4 py-3">{{ student.user.get_full_name|default:student.user.username }}</td>
                    <td class="px-4 py-3">{{ student.department.name|default:"N/A" }}</td>
                    <td class="px-4 py-3">
                        <a href="{% url 'student_update' student.pk %}" class="text-indigo-600 hover:underline mr-3">Edit</a>
                    </td>
                </tr>
                {% empty %}
                <tr><td colspan="4" class="px-4 py-3 text-center text-slate-500">No students found. Add one above.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}"""

# 4. Create Student Form
student_form = """{% extends 'base.html' %}
{% block title %}Add Student{% endblock %}
{% block content %}
<div class="card p-6 max-w-lg mx-auto">
    <h2 class="text-xl font-bold mb-6">Add New Student</h2>
    <form method="post" class="space-y-4">
        {% csrf_token %}
        {{ form.as_p }}
        <div class="flex gap-3 pt-4">
            <button type="submit" class="btn-primary">Save Student</button>
            <a href="{% url 'student_list' %}" class="btn-secondary">Cancel</a>
        </div>
    </form>
</div>
{% endblock %}"""

# 5. Update Fingerprint List with Enroll Button
fp_list = """{% extends 'base.html' %}
{% block title %}Fingerprint Profiles{% endblock %}
{% block content %}
<div class="card p-6">
    <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-bold">Fingerprint Profile Management</h2>
    </div>
    <div class="overflow-x-auto">
        <table class="w-full text-sm text-left">
            <thead class="text-xs uppercase bg-slate-50 text-slate-500">
                <tr><th class="px-4 py-3">Reg Number</th><th class="px-4 py-3">Student Name</th><th class="px-4 py-3">Profile ID</th><th class="px-4 py-3">Status</th><th class="px-4 py-3">Actions</th></tr>
            </thead>
            <tbody>
                {% for student in students %}
                <tr class="border-b bg-white">
                    <td class="px-4 py-3 font-medium">{{ student.registration_number }}</td>
                    <td class="px-4 py-3">{{ student.user.get_full_name|default:student.user.username }}</td>
                    <td class="px-4 py-3">{% if student.fingerprint_profile %}{{ student.fingerprint_profile.profile_id }}{% else %}Not Enrolled{% endif %}</td>
                    <td class="px-4 py-3">
                        {% if student.fingerprint_profile and student.fingerprint_profile.is_active %}
                            <span class="badge-green">Active</span>
                        {% else %}
                            <span class="badge-red">Inactive</span>
                        {% endif %}
                    </td>
                    <td class="px-4 py-3">
                        <form method="post" action="{% url 'fingerprint_enroll' student.pk %}" class="inline">
                            {% csrf_token %}
                            <button type="submit" class="btn-primary btn-sm">Enroll / Update</button>
                        </form>
                    </td>
                </tr>
                {% empty %}
                <tr><td colspan="5" class="px-4 py-3 text-center text-slate-500">No students found.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}"""

templates_to_update = {
    'academics/department_list.html': dept_list,
    'academics/department_form.html': dept_form,
    'accounts/student_list.html': student_list,
    'accounts/student_form.html': student_form,
    'attendance/fingerprint_list.html': fp_list
}

for path, content in templates_to_update.items():
    full_path = os.path.join('templates', path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated/Created: {full_path}")

print("\nFUNCTIONAL FORMS AND BUTTONS ADDED SUCCESSFULLY!")
