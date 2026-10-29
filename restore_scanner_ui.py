import os

scan_html = """{% extends 'base.html' %}
{% block title %}Fingerprint Scanner{% endblock %}
{% block content %}
<div class="min-h-[calc(100vh-4rem)] flex items-center justify-center py-10">
    <div class="w-full max-w-lg bg-white rounded-2xl shadow-lg ring-1 ring-slate-200 p-8 text-center">
        <h1 class="text-2xl font-black text-slate-900 mb-1">Fingerprint Scanner</h1>
        <p class="text-sm text-slate-500 mb-6">Demo Mode: Simulated biometric verification.</p>

        {% if selected_session %}
            <div class="bg-indigo-50 text-indigo-700 rounded-xl px-4 py-3 text-sm font-bold mb-6">
                Session: {{ selected_session.course.course_code }} | Lecturer: {{ selected_session.lecturer.user.get_full_name|default:selected_session.lecturer.user.username }}
            </div>

            <form id="scanForm" method="post" action="{% url 'mark_attendance' selected_session.pk %}">
                {% csrf_token %}
                <div class="mb-6 text-left">
                    <label class="block text-xs font-bold uppercase tracking-widest text-slate-500 mb-2 text-center">Select Student Profile</label>
                    <select name="profile_id" id="profileSelect" class="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-800 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200">
                        <option value="">Select enrolled fingerprint profile...</option>
                        {% for profile in profiles %}
                            <option value="{{ profile.profile_id }}">{{ profile.profile_id }} — {{ profile.student.registration_number }} ({{ profile.student.user.get_full_name|default:profile.student.user.username }})</option>
                        {% endfor %}
                    </select>
                </div>

                <div class="flex justify-center mb-6">
                    <div id="fingerprintBox" class="w-48 h-48 rounded-2xl bg-slate-50 flex items-center justify-center ring-1 ring-slate-200 transition-all duration-500">
                        <svg id="fpIcon" class="w-32 h-32 text-slate-300 transition-all duration-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.07 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.132A8 8 0 008 4.07M3 15.364c.64-1.319 1-2.8 1-4.364 0-1.457.39-2.823 1.07-4"></path>
                        </svg>
                    </div>
                </div>

                <p id="statusText" class="text-sm font-bold text-slate-600 mb-6">Ready. Place finger on scanner.</p>

                <button type="button" id="changeSessionBtn" class="rounded-xl bg-white px-5 py-3 text-base font-semibold text-slate-700 ring-1 ring-slate-300 transition hover:bg-slate-100">Change Session</button>
            </form>
        {% else %}
            <p class="text-slate-600 mb-6">Please select an active session to begin scanning.</p>
            <div class="space-y-3 text-left">
                {% for session in active_sessions %}
                    <a href="{% url 'scan_view' session.pk %}" class="block p-4 bg-slate-50 rounded-xl ring-1 ring-slate-200 hover:ring-indigo-500 transition font-bold text-slate-700">
                        {{ session.course.course_code }} - {{ session.session_date }}
                    </a>
                {% empty %}
                    <p class="text-slate-500 text-center">No active sessions.</p>
                {% endfor %}
            </div>
        {% endif %}
    </div>
</div>

<script>
    const profileSelect = document.getElementById('profileSelect');
    const fpIcon = document.getElementById('fpIcon');
    const fpBox = document.getElementById('fingerprintBox');
    const statusText = document.getElementById('statusText');
    const scanForm = document.getElementById('scanForm');

    profileSelect.addEventListener('change', function() {
        if (this.value) {
            fpBox.className = 'w-48 h-48 rounded-2xl bg-white flex items-center justify-center ring-2 ring-indigo-200 shadow-lg transition-all duration-500';
            fpIcon.className = 'w-32 h-32 text-indigo-600 transition-all duration-500';
            statusText.innerText = 'Scanning... Keep finger steady.';
            statusText.className = 'text-sm font-bold text-indigo-600 mb-6';

            setTimeout(() => {
                const formData = new FormData(scanForm);
                fetch(scanForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        fpBox.className = 'w-48 h-48 rounded-2xl bg-emerald-50 flex items-center justify-center ring-2 ring-emerald-300 shadow-lg transition-all duration-500';
                        fpIcon.className = 'w-32 h-32 text-emerald-500 transition-all duration-500';
                        statusText.innerText = '✅ Success: ' + data.message;
                        statusText.className = 'text-sm font-bold text-emerald-600 mb-6';
                        setTimeout(() => location.reload(), 2000);
                    } else {
                        fpBox.className = 'w-48 h-48 rounded-2xl bg-rose-50 flex items-center justify-center ring-2 ring-rose-300 shadow-lg transition-all duration-500';
                        fpIcon.className = 'w-32 h-32 text-rose-500 transition-all duration-500';
                        statusText.innerText = '❌ Error: ' + data.error;
                        statusText.className = 'text-sm font-bold text-rose-600 mb-6';
                    }
                });
            }, 1500);
        } else {
            fpBox.className = 'w-48 h-48 rounded-2xl bg-slate-50 flex items-center justify-center ring-1 ring-slate-200 transition-all duration-500';
            fpIcon.className = 'w-32 h-32 text-slate-300 transition-all duration-500';
            statusText.innerText = 'Ready. Place finger on scanner.';
            statusText.className = 'text-sm font-bold text-slate-600 mb-6';
        }
    });

    document.getElementById('changeSessionBtn').addEventListener('click', function() {
        window.location.href = "{% url 'session_list' %}";
    });
</script>
{% endblock %}"""

full_path = os.path.join('templates', 'attendance', 'scan.html')
os.makedirs(os.path.dirname(full_path), exist_ok=True)
with open(full_path, 'w', encoding='utf-8') as f:
    f.write(scan_html)
print("PROFESSIONAL SCANNER UI RESTORED SUCCESSFULLY!")
