import os

base_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{% block title %}Attendance Monitoring System{% endblock %}</title>
<script src="https://cdn.tailwindcss.com"></script>
<style type="text/tailwindcss">
@layer components {
  .btn-primary { @apply inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-6 py-3 text-base font-bold text-white shadow-lg shadow-indigo-600/30 transition hover:-translate-y-0.5 hover:bg-indigo-500; }
  .btn-secondary { @apply inline-flex items-center justify-center gap-2 rounded-xl bg-white px-5 py-3 text-base font-semibold text-slate-700 ring-1 ring-slate-300 transition hover:bg-slate-100; }
  .btn-danger { @apply inline-flex items-center justify-center gap-2 rounded-xl bg-rose-600 px-5 py-3 text-base font-bold text-white shadow-lg shadow-rose-600/30 transition hover:bg-rose-500; }
  .btn-sm { @apply px-4 py-2 text-sm; }
  .input { @apply w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-800 placeholder-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200; }
  .label { @apply mb-2 block text-xs font-bold uppercase tracking-widest text-slate-500; }
  .card { @apply rounded-2xl bg-white shadow-sm ring-1 ring-slate-200; }
  .th { @apply px-5 py-3.5 text-left text-xs font-bold uppercase tracking-wider text-slate-500; }
  .td { @apply px-5 py-4 text-sm font-medium text-slate-700; }
  .badge-green { @apply inline-flex items-center rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-700; }
  .badge-red { @apply inline-flex items-center rounded-full bg-rose-100 px-3 py-1 text-xs font-bold text-rose-700; }
  .nav-link { @apply flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-bold text-slate-300 transition hover:bg-slate-800 hover:text-white; }
  .nav-link-active { @apply bg-indigo-600 text-white hover:bg-indigo-600; }
}
</style>
</head>
<body class="bg-slate-100 font-sans text-slate-800 antialiased">

{% if user.is_authenticated and user.role == 'admin' %}
<div class="min-h-screen">
  <div class="fixed inset-x-0 top-0 z-40 flex items-center justify-between bg-slate-900 px-4 py-3 text-white lg:hidden">
    <span class="text-lg font-black tracking-tight">Attendance Console</span>
    <button onclick="document.getElementById('sidebar').classList.toggle('hidden')" class="rounded-lg bg-slate-800 px-4 py-2 text-sm font-bold">Menu</button>
  </div>

  <aside id="sidebar" class="fixed inset-y-0 left-0 z-30 hidden w-72 flex-col bg-slate-900 pt-14 lg:flex lg:pt-0">
    <div class="flex h-20 items-center gap-3 border-b border-slate-800 px-6">
      <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-600 text-xl font-black text-white">S</div>
      <div>
        <p class="text-base font-black leading-tight text-white">Attendance Monitor</p>
        <p class="text-xs font-semibold uppercase tracking-widest text-indigo-400">Management Console</p>
      </div>
    </div>
    <nav class="flex-1 space-y-1.5 overflow-y-auto px-4 py-6">
      <a href="{% url 'dashboard' %}" class="nav-link {% if request.resolver_match.url_name == 'dashboard' %}nav-link-active{% endif %}"><span>📊</span> Dashboard</a>
      <a href="{% url 'student_list' %}" class="nav-link {% if 'student' in request.resolver_match.url_name %}nav-link-active{% endif %}"><span>🎓</span> Students</a>
      <a href="{% url 'lecturer_list' %}" class="nav-link {% if 'lecturer' in request.resolver_match.url_name %}nav-link-active{% endif %}"><span>👨‍🏫</span> Lecturers</a>
      <a href="{% url 'department_list' %}" class="nav-link {% if 'department' in request.resolver_match.url_name %}nav-link-active{% endif %}"><span>🏛️</span> Departments</a>
      <a href="{% url 'course_list' %}" class="nav-link {% if 'course' in request.resolver_match.url_name %}nav-link-active{% endif %}"><span>📚</span> Courses</a>
      <a href="{% url 'enrollment_list' %}" class="nav-link {% if 'enrollment' in request.resolver_match.url_name %}nav-link-active{% endif %}"><span>🔗</span> Enrollments</a>
      <div class="my-4 border-t border-slate-800"></div>
      <a href="{% url 'fingerprint_list' %}" class="nav-link {% if 'fingerprint' in request.resolver_match.url_name %}nav-link-active{% endif %}"><span>👆</span> Fingerprint Profiles</a>
      <a href="{% url 'session_list' %}" class="nav-link {% if 'session' in request.resolver_match.url_name %}nav-link-active{% endif %}"><span>⏱️</span> Sessions</a>
      <a href="{% url 'report_dashboard' %}" class="nav-link {% if 'report' in request.resolver_match.url_name %}nav-link-active{% endif %}"><span>📈</span> Reports</a>
    </nav>
    <div class="border-t border-slate-800 p-4">
      <div class="mb-3 rounded-xl bg-slate-800 px-4 py-3">
        <p class="text-sm font-bold text-white">{{ user.username }}</p>
        <p class="text-xs font-semibold text-indigo-300">System Manager</p>
      </div>
      <form method="post" action="{% url 'logout' %}">
        {% csrf_token %}
        <button type="submit" class="w-full rounded-xl bg-rose-600/90 px-4 py-3 text-sm font-bold text-white transition hover:bg-rose-600">Sign Out</button>
      </form>
    </div>
  </aside>

  <div class="pt-14 lg:pl-72 lg:pt-0">
    <main class="mx-auto max-w-7xl px-4 py-8 lg:px-8">

{% elif user.is_authenticated %}
<div class="min-h-screen">
  <header class="bg-slate-900 text-white">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-4">
      <span class="text-lg font-black tracking-tight">Attendance Monitoring System</span>
      <div class="flex items-center gap-4">
        <span class="hidden text-sm font-bold text-slate-300 sm:inline">{{ user.username }} ({{ user.get_role_display }})</span>
        <form method="post" action="{% url 'logout' %}">
          {% csrf_token %}
          <button type="submit" class="rounded-lg bg-rose-600 px-4 py-2 text-sm font-bold">Sign Out</button>
        </form>
      </div>
    </div>
  </header>
  <main class="mx-auto max-w-7xl px-4 py-8">

{% else %}
<main class="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 p-4">
{% endif %}

      {% if messages %}
      <div class="mb-6 space-y-3">
        {% for message in messages %}
        <div class="rounded-xl px-5 py-4 text-sm font-bold shadow-sm {% if 'success' in message.tags %}bg-emerald-100 text-emerald-800 ring-1 ring-emerald-300{% elif 'danger' in message.tags %}bg-rose-100 text-rose-800 ring-1 ring-rose-300{% elif 'warning' in message.tags %}bg-amber-100 text-amber-800 ring-1 ring-amber-300{% else %}bg-sky-100 text-sky-800 ring-1 ring-sky-300{% endif %}">
          {{ message }}
        </div>
        {% endfor %}
      </div>
      {% endif %}

      {% block content %}{% endblock %}

{% if user.is_authenticated and user.role == 'admin' %}
    </main>
  </div>
</div>

{% elif user.is_authenticated %}
  </main>
</div>

{% else %}
</main>
{% endif %}

</body>
</html>"""

os.makedirs('templates', exist_ok=True)
with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(base_html)
print('ORIGINAL BASE TEMPLATE RESTORED SUCCESSFULLY!')
