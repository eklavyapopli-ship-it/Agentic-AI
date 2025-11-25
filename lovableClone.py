from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
load_dotenv()

client = genai.Client(
    api_key=os.getenv('GEMINI_API_KEY')
)
prompt = '''
You are an AI Web App Generator.  
Your job is to generate a SINGLE file named `index.html` based on the user requirement.

### FOLLOW THESE RULES STRICTLY:
1. Return ONLY valid HTML code.
2. Do NOT include markdown formatting like ```html or ``` anywhere.
3. Use internal CSS inside <style>...</style>.
4. Use internal JavaScript inside <script>...</script>.
5. No external links, no external JS/CSS files.
6. Do not skip any part of the UI or functionality.
7. The output must open correctly in a browser without needing any other files.
8. Include responsive design (mobile-friendly).
9. JavaScript must contain all required logic for interactivity.
10. Do not write explanations, notes, or extra text—ONLY the final index.html.

### STRUCTURE YOU MUST FOLLOW:
<html>
<head>
<title>[Auto-generate based on app]</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  /* Internal CSS */
</style>
</head>
<body>
  <!-- Auto-generated UI based on the user's description -->
  
<script>
  // Internal JavaScript
</script>
</body>
</html>

### USER REQUIREMENT:
[INSERT USER REQUEST HERE]

'''
response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=prompt),
    contents='''Build a modern single-page website called “TaskMaster Pro”.

The website should include:

1. A clean hero section with:
   - Title: “TaskMaster Pro”
   - Subtitle: “Smart Productivity for Everyone”
   - A “Start Now” button that scrolls to the main section.

2. Main Section:
   - A task manager where users can:
     • Add new tasks
     • Mark tasks as complete
     • Delete tasks
     • Filter tasks (All / Completed / Pending)
     Add some pseudo data also that u feel is good, connect internet images, add some image cards etc and make professional

3. UI/Design Requirements:
   - Use a dark theme But make it look professional.
   - Smooth animations for:
       • Button hover
       • New task appearing
       • Task deletion
   - Responsive layout for mobile and desktop.
   Add some pseudo data also that u feel is good, connect internet images, add some image cards etc and make professional

4. JavaScript Requirements:
   - Store tasks in browser localStorage.
   - On page load, load all saved tasks.
   - Update localStorage when tasks change.
   - Use pure JavaScript (no libraries).

5. Return everything inside a single `index.html` file with internal CSS and JS.
'''
)

f = open("index.html", "w")
f.write(response.text)