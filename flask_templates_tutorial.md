# Flask Templates Tutorial: Building a Simple LLM Chat Interface

## What Are Flask Templates?

Flask templates are HTML files that can display dynamic content. Instead of writing static HTML, templates let you:
- Insert Python variables into HTML
- Use loops and conditions in HTML
- Create reusable layouts that multiple pages can share
- Keep your HTML separate from your Python code

Think of templates as HTML pages with "blanks" that Flask fills in with real data.

## Project Structure

```
your-project/
├── app.py                 # Your main Flask application
├── templates/            # Folder where Flask looks for HTML templates
│   ├── template.html     # Base layout that other pages extend
│   └── index.html        # Home page that extends the base layout
└── requirements.txt      # Python dependencies
```

**Important:** Flask automatically looks for templates in a folder called `templates/` - the name matters!

## The Base Template (template.html)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}LLM Chat App{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
            <div class="container-fluid">
                <a class="navbar-brand" href="/">LLM Chat</a>
                <div class="navbar-nav">
                    <a class="nav-link" href="/">Chat</a>
                    <a class="nav-link" href="/history">History</a>
                </div>
            </div>
        </nav>
        
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

### Key Template Concepts:

1. **`{% block title %}`** - Creates a "slot" that other templates can fill in
2. **`{% block content %}`** - Another "slot" for the main page content
3. **`{% endblock %}`** - Closes each block
4. This template provides the common structure (navigation, CSS, etc.) that all pages share

## The Home Page Template (index.html)

```html
{% extends "template.html" %}

{% block title %}LLM Chat - Home{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h3 class="mb-0">Ask the AI Anything</h3>
            </div>
            <div class="card-body">
                <form action="/chat" method="POST">
                    <div class="mb-3">
                        <label for="question" class="form-label">Your Question:</label>
                        <textarea class="form-control" id="question" name="question" rows="4" 
                                placeholder="Type your question here..." required></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">Ask AI</button>
                </form>
            </div>
        </div>
        
        {% if response %}
        <div class="card mt-4">
            <div class="card-header">
                <h5 class="mb-0">AI Response</h5>
            </div>
            <div class="card-body">
                <p><strong>Your Question:</strong> {{ question }}</p>
                <hr>
                <p><strong>AI Answer:</strong></p>
                <div class="bg-light p-3 rounded">{{ response }}</div>
            </div>
        </div>
        {% endif %}
        
        {% if error %}
        <div class="alert alert-danger mt-4" role="alert">
            <strong>Error:</strong> {{ error }}
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}
```

### Key Template Concepts:

1. **`{% extends "template.html" %}`** - This template "inherits" from the base template
2. **`{{ variable_name }}`** - Displays a Python variable in the HTML
3. **`{% if condition %}`** - Only shows HTML if the condition is true
4. **`{% endif %}`** - Closes the if statement
5. **Form action="/chat"** - When submitted, sends data to the `/chat` route in your Flask app

## The Python Code (app.py changes)

Here are the key changes made to connect the templates to your Flask app:

### 1. Simple Home Route
```python
@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')
```

**What this does:** When someone visits your website's home page (`/`), Flask renders the `index.html` template and sends it to their browser.

### 2. Chat Processing Route
```python
@app.route('/chat', methods=['POST'])
def chat():
    """Handle LLM chat requests"""
    question = request.form.get('question')
    
    if not question:
        return render_template('index.html', error="Please enter a question.")
    
    try:
        API = os.getenv("AI_API_KEY")
        if not API:
            return render_template('index.html', 
                                 question=question,
                                 error="AI API key not found.")
        
        client = genai.Client(api_key=API)
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=question
        )
        
        return render_template('index.html', 
                             question=question,
                             response=response.text)
        
    except Exception as e:
        return render_template('index.html', 
                             question=question,
                             error=f"Error getting AI response: {e}")
```

**What this does:**
1. Gets the question from the HTML form
2. Sends it to the AI
3. Renders the same template again, but now with variables filled in:
   - `question` - shows what the user asked
   - `response` - shows the AI's answer
   - `error` - shows any error messages

## How It All Works Together

1. **User visits `/`** → Flask calls `index()` → Renders `index.html` (which extends `template.html`)

2. **User types question and clicks "Ask AI"** → Form submits to `/chat` → Flask calls `chat()`

3. **Flask processes the question** → Gets AI response → Renders `index.html` again with the response data

4. **Template displays the response** → User sees their question and the AI's answer on the same page

## Template Inheritance Explained

Think of template inheritance like this:

- `template.html` is like a picture frame - it has the border and structure
- `index.html` is like the photo - it fills in the actual content
- Flask combines them to create the final webpage

The `{% extends %}` command tells Flask: "Take everything from the base template, but replace the `{% block %}` sections with my content."

## Key Flask Template Rules

1. **Templates go in `templates/` folder** - Flask looks there automatically
2. **Use `{{ variable }}` to display Python data** in HTML
3. **Use `{% command %}` for logic** (if statements, loops, extends, blocks)
4. **Always close blocks** with `{% endblock %}`
5. **Pass data to templates** using `render_template('page.html', variable=value)`

## Common Beginner Mistakes

❌ **Wrong:** `<p>Hello variable</p>` - This just shows the word "variable"
✅ **Correct:** `<p>Hello {{ variable }}</p>` - This shows the actual value

❌ **Wrong:** Forgetting to close blocks
✅ **Correct:** Every `{% block %}` needs `{% endblock %}`

❌ **Wrong:** Templates in wrong folder
✅ **Correct:** Templates must be in `templates/` folder

This simple setup gives you a working chat interface where users can ask questions and get AI responses, all while learning the fundamentals of Flask templates!