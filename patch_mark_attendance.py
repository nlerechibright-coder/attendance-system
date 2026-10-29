import os
p = os.path.join('attendance', 'views.py')
with open(p, 'r', encoding='utf-8', newline='') as f:
    content = f.read()
content = content.replace('\r\n', '\n')

old = (
    "    try:\n"
    "        data = json.loads(request.body)\n"
    "        profile_id = data.get('profile_id')\n"
    "    except json.JSONDecodeError: profile_id = request.POST.get('profile_id')\n"
)
new = (
    "    content_type = request.content_type or ''\n"
    "    if 'application/json' in content_type:\n"
    "        try:\n"
    "            data = json.loads(request.body)\n"
    "            profile_id = data.get('profile_id')\n"
    "        except (json.JSONDecodeError, ValueError):\n"
    "            profile_id = None\n"
    "    else:\n"
    "        profile_id = request.POST.get('profile_id')\n"
)

if old in content:
    content = content.replace(old, new)
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('PATCHED mark_attendance: form-safe body reading.')
else:
    print('BLOCK NOT FOUND - printing nearby lines for diagnosis:')
    for i, l in enumerate(content.split('\n')):
        if 'json.loads(request.body)' in l or 'profile_id = request.POST' in l or 'def mark_attendance' in l:
            print(i + 1, repr(l))
