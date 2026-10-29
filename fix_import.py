with open('attendance/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the import path
content = content.replace('from accounts.decorators import admin_required', 'from accounts.views import admin_required')

with open('attendance/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("IMPORT FIXED IN ATTENDANCE VIEWS!")
