import os

scan_html = r"""{% extends 'base.html' %}
{% block title %}Fingerprint Scanner{% endblock %}
{% block content %}
<style>
.fp-box{position:relative;width:12rem;height:12rem;border-radius:1rem;display:flex;align-items:center;justify-content:center;overflow:hidden;user-select:none;border:0;transition:background-color .3s,box-shadow .3s;}
.fp-box .fp-icon{width:8rem;height:8rem;position:relative;z-index:10;transition:color .3s,transform .3s;}
.fp-tint{position:absolute;inset:0;z-index:1;opacity:0;pointer-events:none;transition:opacity .3s;background:radial-gradient(circle at 50% 50%,rgba(99,102,241,.14),transparent 70%);}
.fp-line{position:absolute;left:0;right:0;top:0;height:44px;z-index:20;pointer-events:none;opacity:0;background:linear-gradient(to bottom,rgba(99,102,241,0) 0%,rgba(99,102,241,0) 32%,rgba(129,140,248,.85) 49%,rgba(224,231,255,1) 50%,rgba(129,140,248,.85) 51%,rgba(99,102,241,0) 68%,rgba(99,102,241,0) 100%);box-shadow:0 0 16px 3px rgba(99,102,241,.5);}
.fp-ready{background:#f8fafc;box-shadow:0 0 0 1px #e2e8f0;cursor:not-allowed;}
.fp-ready .fp-icon{color:#cbd5e1;}
.fp-armed{background:#eef2ff;box-shadow:0 0 0 2px #c7d2fe;cursor:pointer;animation:fpInvite 1.6s ease-in-out infinite;}
.fp-armed .fp-icon{color:#818cf8;}
.fp-scanning{background:#ffffff;box-shadow:0 0 0 2px #a5b4fc,0 12px 32px -12px rgba(99,102,241,.5);cursor:wait;}
.fp-scanning .fp-icon{color:#4f46e5;}
.fp-scanning .fp-tint{opacity:1;}
.fp-scanning .fp-line{opacity:1;animation:fpSweep .9s linear infinite alternate;}
.fp-success{background:#ecfdf5;box-shadow:0 0 0 2px #6ee7b7,0 12px 32px -12px rgba(16,185,129,.45);cursor:pointer;}
.fp-success .fp-icon{color:#10b981;}
.fp-error{background:#fff1f2;box-shadow:0 0 0 2px #fda4af,0 12px 32px -12px rgba(244,63,94,.45);cursor:pointer;}
.fp-error .fp-icon{color:#f43f5e;}
.fp-pop .fp-icon{animation:fpPop .5s ease;}
.fp-shake .fp-icon{animation:fpShake .5s ease;}
@keyframes fpSweep{from{transform:translateY(-44px);}to{transform:translateY(192px);}}
@keyframes fpInvite{0%,100%{transform:scale(1);}50%{transform:scale(1.035);}}
@keyframes fpPop{0%{transform:scale(1);}45%{transform:scale(1.14);}100%{transform:scale(1);}}
@keyframes fpShake{10%,90%{transform:translateX(-2px);}20%,80%{transform:translateX(3px);}30%,50%,70%{transform:translateX(-6px);}40%,60%{transform:translateX(6px);}}
</style>

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
                <button type="button" id="fingerprintBox" class="fp-box fp-ready" aria-label="Scan fingerprint">
                    <span class="fp-tint"></span>
                    <span class="fp-line"></span>
                    <svg class="fp-icon" id="fpIcon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
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
    var sel = document.getElementById('profileSelect');
    var box = document.getElementById('fingerprintBox');
    var status = document.getElementById('statusText');
    var scanUrl = document.getElementById('scanUrl');
    var csrf = document.getElementById('csrfToken');
    if (!sel || !box || !scanUrl) return;

    var busy = false;
    var READY_TEXT = 'Select a student, then tap the fingerprint to scan.';
    var ARMED_TEXT = 'Ready. Tap the fingerprint to scan.';
    var SCAN_TEXT = 'Scanning... Keep finger steady.';
    var MIN_SCAN_MS = 1800;

    function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

    function visual(state) {
        box.className = 'fp-box fp-' + state;
        box.disabled = (state === 'scanning');
    }
    function setStatus(text, colorClass) {
        status.innerText = text;
        status.className = 'text-sm font-bold mb-6 ' + colorClass;
    }
    function addTemp(cls, ms) {
        box.classList.add(cls);
        setTimeout(function () { box.classList.remove(cls); }, ms);
    }

    sel.addEventListener('change', function () {
        if (busy) return;
        if (this.value) { visual('armed'); setStatus(ARMED_TEXT, 'text-indigo-600'); }
        else { visual('ready'); setStatus(READY_TEXT, 'text-slate-600'); }
    });

    async function doFetch(profileId) {
        var fd = new FormData();
        fd.append('profile_id', profileId);
        fd.append('csrfmiddlewaretoken', csrf.value);
        return fetch(scanUrl.value, {
            method: 'POST',
            body: fd,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
    }

    async function parse(resp) {
        var ct = resp.headers.get('content-type') || '';
        if (ct.indexOf('application/json') !== -1) {
            var d = await resp.json();
            return { ok: !!(d && d.success), message: (d && d.message) || 'Attendance marked successfully.', error: (d && d.error) || 'Scan failed.' };
        }
        var t = await resp.text();
        var clean = t.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 160);
        return { ok: false, error: clean || ('HTTP ' + resp.status) };
    }

    box.addEventListener('click', async function () {
        if (busy) return;
        var profileId = sel.value;

        if (!profileId) {
            addTemp('fp-shake', 500);
            setStatus('Select a student first.', 'text-rose-600');
            setTimeout(function () { if (!sel.value) { visual('ready'); setStatus(READY_TEXT, 'text-slate-600'); } }, 1200);
            return;
        }

        busy = true;
        visual('scanning');
        setStatus(SCAN_TEXT, 'text-indigo-600');

        var out;
        try {
            var pair = await Promise.all([doFetch(profileId), sleep(MIN_SCAN_MS)]);
            out = await parse(pair[0]);
        } catch (e) {
            out = { ok: false, error: (e && e.message) || 'Network/server error.' };
        }
        busy = false;

        if (out.ok) {
            visual('success');
            addTemp('fp-pop', 500);
            setStatus('\u2713 ' + out.message, 'text-emerald-600');
            setTimeout(function () {
                var opt = sel.querySelector('option[value="' + profileId + '"]');
                if (opt) opt.disabled = true;
                sel.selectedIndex = 0;
                visual('ready');
                setStatus(READY_TEXT, 'text-slate-600');
            }, 1500);
        } else {
            visual('error');
            addTemp('fp-shake', 500);
            setStatus('\u2715 ' + out.error, 'text-rose-600');
            setTimeout(function () { visual('armed'); setStatus(ARMED_TEXT, 'text-indigo-600'); }, 2200);
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
print("SCANNER REPLACED: moving down-up beam + green pop")
