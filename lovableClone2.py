from google import genai
from pydantic import BaseModel, Field
from google.genai import types
from typing import List, Optional
import os
from typing import Union, Literal
from dotenv import load_dotenv
load_dotenv()
class Type(BaseModel):
    file_type: Literal["html", "css","js"] = Field(description="The type of the file")
    content: str = Field(description="Full Code of That particular file_type")

class Recipe(BaseModel):
    recipe_name: str = Field(description="The name of the recipe.")
    files: List[Type]

client = genai.Client(
    api_key= os.getenv('GEMINI_API_KEY')
)

prompt = """
You are an AI Web App Generator.  
Your job is to generate a SINGLE file named `index.html` based on the user requirement.

### FOLLOW THESE RULES STRICTLY:
1. Return ONLY valid HTML, CSS AND JS code.
2. Do NOT include markdown formatting like ```html or ``` anywhere.
3. Use external CSS  <style>...</style>.
4. Use external JavaScript  <script>...</script>.
5. Do not skip any part of the UI or functionality.
6. The output must open correctly in a browser without needing any other files.
7. Include responsive design (mobile-friendly).
8. JavaScript must contain all required logic for interactivity.
9. Do not write explanations, notes, or extra text—ONLY the final index.html.

### STRUCTURE YOU MUST FOLLOW:
<html>
<head>
<title>[Auto-generate based on app]</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="style.css">
</head>
<body>
  <!-- Auto-generated UI based on the user's description -->
  
<script src="script.js">
</script>
</body>
</html>

### USER REQUIREMENT:
[INSERT USER REQUEST HERE]
"""

inst = '''
Build a modern single-page website called “TaskMaster Pro”.

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

3. UI/Design Requirements:
   - Use a dark theme (black/grey) with neon green highlights.
   - Smooth animations for:
       • Button hover
       • New task appearing
       • Task deletion
   - Responsive layout for mobile and desktop.

4. JavaScript Requirements:
   - Store tasks in browser localStorage.
   - On page load, load all saved tasks.
   - Update localStorage when tasks change.
   - Use pure JavaScript (no libraries).

5. Return everything as seperate html, css and js files
Also make all files systematic and clean, like they all should be formatted properly. Many times, your javascript generated file is not properly formatted due to which the js file comes in a single line which ruins the code
'''

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=inst,
    config={
        "response_mime_type": "application/json",
        "response_json_schema": Recipe.model_json_schema(),
        "system_instruction": types.GenerateContentConfig(
            system_instruction=prompt
        ),
    },
)

recipe = Recipe.model_validate_json(response.text)
print(recipe)

if recipe.files[0].file_type == "html":
    f = open("index.html", "w")
    f.write(recipe.files[0].content)
    recipe.files.pop(0)
if recipe.files[0].file_type == "css":
    f = open("style.css", "w")
    f.write(recipe.files[0].content)
    recipe.files.pop(0)
if recipe.files[0].file_type == "js":
    f = open("script.js", "w")
    f.write(recipe.files[0].content)


