# Ace Designers CIP Management System
==================================

Prerequisites
------------
1. Python Installation:
   - Download Python 3.12: https://www.python.org/downloads/
   - Run installer
   - CHECK "Add Python to PATH" box during installation
   - Click "Install Now"

Setup Instructions
----------------
1. Extract the Project:
   - Right-click the ZIP file
   - Select "Extract All"
   - Choose location (e.g., Desktop)
   - Click "Extract"

2. Open Command Prompt:
   - Press Windows + R
   - Type "cmd"
   - Click OK
   - Type EXACTLY: cd C:\Users\[YourUsername]\Desktop\Ace_kaizen_project\kaizen_project\kaizen_project\django_backend
   - Replace [YourUsername] with your Windows username

3. Run Setup:
   - Double-click setup.bat
   OR
   Run these commands manually in order:
   - python -m venv env
   - env\Scripts\activate
   - pip install -r requirements.txt
   - python manage.py migrate
   - python manage.py loaddata data.json
   - python manage.py runserver

Accessing the System
------------------
1. Open web browser
2. Go to: http://127.0.0.1:8000

Test Credentials (register new users)
--------------
1. HOD Login:
   - Username: hod
   - Password: password123

2. Employee Login:
   - Username: employee
   - Password: password123

3. Coordinator Login:
   - Username: coordinator
   - Password: password123

4. Finance Login:
   - Username: finance
   - Password: password123

Troubleshooting
-------------
1. If "python not found":
   - Reinstall Python
   - Ensure "Add Python to PATH" is checked

2. If port error:
   - Close other applications using port 8000
   - Or use: python manage.py runserver 8080

3. If database error:
   - Delete db.sqlite3 file
   - Run: python manage.py migrate
   - Run: python manage.py loaddata data.json

Stopping the Server
-----------------
- Close the command prompt window
- Or press Ctrl+C in command prompt

Support Contact
-------------
For technical assistance contact:
[Your Contact Information]

Note: This is a test version for evaluation purposes.