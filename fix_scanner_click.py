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

            <input type="hidden" id="scanUrl" value="{% url 'mark_attendance' selected_session.pk %}">
            <input type="hidden" id="csrfToken" value="{{ csrf_token }}">

            <div class="mb-6 text-left">
                <label class="block text-xs font-bold uppercase tracking-widest text-slate-500 mb-2 text-center">Select Student Profile</label>
                <select id="profileSelect" class="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-800 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200">
                    <option value="">Select enrolled fingerprint profile...</option>
                    {% for profile in profiles %}
                        <option value="{{ profile.profile_id }}">{{ profile.profile_id }} — {{ profile.student.registration_number }} ({{ profile.student.user.get_full_name|default:profile.student.user.username }})</option>
                    {% endfor %}
                </select>
            </div>

            <div class="flex justify-center mb-6">
                <button type="button" id="fingerprintBox" aria-label="Scan fingerprint"
                    class="w-48 h-48 rounded-2xl bg-slate-50 flex items-center justify-center ring-1 ring-slate-200 transition-all duration-300 cursor-not-allowed select-none">
                    <svg id="fpIcon" class="w-32 h-32 text-slate-300 transition-all duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.07 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.132A8 8 0 008 4.07M3 15.364c.64-1.319 1-2.8 1-4.364 0-1.457.39-2.823 1.07-4"></path>
                    </svg>
                </button>
            </div>

            <p id="statusText" class="text-sm font-bold text-slate-600 mb-6">Select a student, then tap the fingerprint to scan.</p>

            <a href="{% url 'session_list' %}" class="inline-block rounded-xl bg-white px-5 py-3 text-base font-semibold text-slate-700 ring-1 ring-slate-300 transition hover:bg-slate-100">Change Session</a>
        {% else %}
            <p class="text-slate-600 mb-6">Please select an active session to begin scanning.</p>
            <div class="space-y-3 text-left">
                {% for session in active_sessions %}
                    <a href="{% url 'scan_view' session.pk %}" class="block p-4 bg-slate-50 rounded-xl ring-1 ring-slate-200 hover:ring-indigo-500 transition font-bold text-slate-700">
                        {{ session.course.course_code }} - {{ session.session_date }}
                    </a>
                {% empty %}
                    <p class="text-slate-500 text-center">No active sessions. Start one from a course.</p>
                {% endfor %}
            </div>
        {% endif %}
    </div>
</div>

<script>
(function () {
    const sel = document.getElementById('profileSelect');
    const box = document.getElementById('fingerprintBox');
    const icon = document.getElementById('fpIcon');
    const status = document.getElementById('statusText');
    const scanUrl = document.getElementById('scanUrl');
    const csrf = document.getElementById('csrfToken');
    if (!sel || !box) return;

    let busy = false;

    function visual(state) {
        box.disabled = (state === 'scanning');
        if (state === 'ready') {
            box.className = 'w-48 h-48 rounded-2xl bg-slate-50 flex items-center justify-center ring-1 ring-slate-200 transition-all duration-300 cursor-pointer select-none';
            icon.className = 'w-32 h-32 text-slate-300 transition-all duration-300';
        } else if (state === 'armed') {
            box.className = 'w-48 h-48 rounded-2xl bg-indigo-50 flex items-center justify-center ring-2 ring-indigo-200 transition-all duration-300 cursor-pointer select-none animate-pulse';
            icon.className = 'w-32 h-32 text-indigo-400 transition-all duration-300';
        } else if (state === 'scanning') {
            box.className = 'w-48 h-48 rounded-2xl bg-white flex items-center justify-center ring-2 ring-indigo-300 shadow-lg transition-all duration-300 cursor-wait select-none';
            icon.className = 'w-32 h-32 text-indigo-600 transition-all duration-300';
        } else if (state === 'success') {
            box.className = 'w-48 h-48 rounded-2xl bg-emerald-50 flex items-center justify-center ring-2 ring-emerald-300 shadow-lg transition-all duration-300 cursor-pointer select-none';
            icon.className = 'w-32 h-32 text-emerald-500 transition-all duration-300';
        } else if (state === 'error') {
            box.className = 'w-48 h-48 rounded-2xl bg-rose-50 flex items-center justify-center ring-2 ring-rose-300 shadow-lg transition-all duration-300 cursor-pointer select-none';
            icon.className = 'w-32 h-32 text-rose-500 transition-all duration-300';
        }
    }

    function setStatus(text, color) {
        status.innerText = text;
        status.className = 'text-sm font-bold mb-6 ' + color;
    }

    // Choosing a student only ARMS the scanner; it does not fire the request.
    sel.addEventListener('change', function () {
        if (busy) return;
        if (this.value) {
            visual('armed');
            setStatus('Ready. Tap the fingerprint to scan.', 'text-indigo-600');
        } else {
            visual('ready');
            setStatus('Select a student, then tap the fingerprint to scan.', 'text-slate-600');
        }
    });

    // Clicking the fingerprint is what performs the scan.
    box.addEventListener('click', async function () {
        if (busy) return;
        const profileId = sel.value;
        if (!profileId) {
            visual('error');
            setStatus('Select a student first.', 'text-rose-600');
            setTimeout(() => { visual('ready'); setStatus('Select a student, then tap the fingerprint to scan.', 'text-slate-600'); }, 1500);
            return;
        }

        busy = true;
        visual('scanning');
        setStatus('Scanning... Keep finger steady.', 'text-indigo-600');

        try {
            await new Promise(r => setTimeout(r, 1200)); // simulated capture time

            const fd = new FormData();
            fd.append('profile_id', profileId);
            fd.append('csrfmiddlewaretoken', csrf.value);

            const res = await fetch(scanUrl.value, {
                method: 'POST',
                body: fd,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });

            const ct = res.headers.get('content-type') || '';
            let data;
            if (ct.includes('application/json')) {
                data = await res.json();
            } else {
                const txt = await res.text();
                throw new Error(txt.replace(/<[^>]*>/g, ' ').trim().slice(0, 160) || ('HTTP ' + res.status));
            }

            if (data && data.success) {
                visual('success');
                setStatus('\\u2713 ' + (data.message || 'Attendance marked successfully.'), 'text-emerald-600');
                const opt = sel.querySelector('option[value="' + profileId + '"]');
                if (opt) opt.disabled = true;          // prevent duplicate scan -> no red later
                sel.selectedIndex = 0;
                setTimeout(() => { visual('armed'); setStatus('Tap the fingerprint to scan the next student.', 'text-indigo-600'); if (!sel.value) visual('ready'); }, 1600);
            } else {
                visual('error');
                setStatus('\\u2715 ' + ((data && data.error) || 'Scan failed.'), 'text-rose-600');
                setTimeout(() => { visual('armed'); setStatus('Ready. Tap the fingerprint to scan.', 'text-indigo-600'); }, 2200);
            }
        } catch (err) {
            visual('error');
            setStatus('\\u2715 ' + (err.message || 'Network/server error.'), 'text-rose-600');
            setTimeout(() => { visual('armed'); setStatus('Ready. Tap the fingerprint to scan.', 'text-indigo-600'); }, 2500);
        } finally {
            busy = false;
        }
    });

    visual('ready');
})();
</script>
{% endblock %}"""

full_path = os.path.join('templates', 'attendance', 'scan.html')
os.makedirs(os.path.dirname(full_path), exist_ok=True)
with open(full_path, 'w', encoding='utf-8') as f:
    f.write(scan_html)
print("SCANNER REPLACED: click-to-scan + full error handling")
