import os

# Ensure the template directories exist
os.makedirs('templates/accounts', exist_ok=True)
os.makedirs('templates/dashboard', exist_ok=True)

# 1. Base Template
base_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Attendance System{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-100 font-sans text-slate-800 antialiased">
    <main class="flex min-h-screen items-center justify-center p-4">
        <div class="w-full max-w-md">
            {% if messages %}
            <div class="mb-6 space-y-3">
                {% for message in messages %}
                <div class="rounded-xl px-5 py-4 text-sm font-bold shadow-sm {% if 'success' in message.tags %}bg-emerald-100 text-emerald-800{% else %}bg-rose-100 text-rose-800{% endif %}">
                    {{ message }}
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% block content %}{% endblock %}
        </div>
    </main>
</body>
</html>
"""

# 2. Login Template
login_html = """{% extends 'base.html' %}
{% block title %}Login - Attendance System{% endblock %}
{% block content %}
<div class="rounded-2xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
    <div class="mb-6 text-center">
        <h1 class="text-2xl font-black text-slate-900">Management Login</h1>
        <p class="text-sm text-slate-500">Enter your credentials to access the dashboard</p>
    </div>
    <form method="post" class="space-y-4">
        {% csrf_token %}
        <div>
            <label class="mb-2 block text-xs font-bold uppercase tracking-widest text-slate-500">Username</label>
            <input type="text" name="username" required class="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-800 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200" placeholder="admin">
        </div>
        <div>
            <label class="mb-2 block text-xs font-bold uppercase tracking-widest text-slate-500">Password</label>
            <input type="password" name="password" required class="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-800 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200" placeholder="••••••••">
        </div>
        <button type="submit" class="w-full rounded-xl bg-indigo-600 px-6 py-3 text-base font-bold text-white shadow-lg shadow-indigo-600/30 transition hover:bg-indigo-500">
            Sign In
        </button>
    </form>
</div>
{% endblock %}
"""

# 3. Admin Dashboard Template (Placeholder to verify login)
admin_dashboard_html = """{% extends 'base.html' %}
{% block title %}Admin Dashboard{% endblock %}
{% block content %}
<div class="rounded-2xl bg-white p-8 shadow-sm ring-1 ring-slate-200 w-full max-w-4xl">
    <div class="mb-6 flex items-center justify-between border-b border-slate-200 pb-4">
        <h1 class="text-2xl font-black text-slate-900">Administrator Dashboard</h1>
        <form method="post" action="{% url 'logout' %}">
            {% csrf_token %}
            <button type="submit" class="rounded-xl bg-rose-600 px-4 py-2 text-sm font-bold text-white transition hover:bg-rose-500">Sign Out</button>
        </form>
    </div>
    <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div class="rounded-xl bg-indigo-50 p-6 text-center">
            <p class="text-3xl font-black text-indigo-600">{{ total_students|default:"0" }}</p>
            <p class="text-sm font-bold uppercase text-slate-500">Total Students</p>
        </div>
        <div class="rounded-xl bg-emerald-50 p-6 text-center">
            <p class="text-3xl font-black text-emerald-600">{{ total_lecturers|default:"0" }}</p>
            <p class="text-sm font-bold uppercase text-slate-500">Total Lecturers</p>
        </div>
        <div class="rounded-xl bg-amber-50 p-6 text-center">
            <p class="text-3xl font-black text-amber-600">{{ active_sessions|default:"0" }}</p>
            <p class="text-sm font-bold uppercase text-slate-500">Active Sessions</p>
        </div>
    </div>
    <div class="mt-8 rounded-xl bg-slate-50 p-6 text-center">
        <p class="text-slate-600">✅ <strong>Success!</strong> You are logged into the custom management dashboard.</p>
        <p class="mt-2 text-sm text-slate-500">The system is ready for Railway deployment.</p>
    </div>
</div>
{% endblock %}
"""

with open('templates/base.html', 'w', encoding='utf-8') as f: f.write(base_html)
with open('templates/accounts/login.html', 'w', encoding='utf-8') as f: f.write(login_html)
with open('templates/dashboard/admin_dashboard.html', 'w', encoding='utf-8') as f: f.write(admin_dashboard_html)

print('TEMPLATES CREATED SUCCESSFULLY!')
