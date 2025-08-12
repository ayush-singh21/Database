from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import os
from dotenv import load_dotenv
from google import genai
import sqlite3

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Global variable to store the dataframe
df = None

def load_data():
    """Load the Excel file into a dataframe"""
    global df
    file_path = "./Spreadsheet/ProjectTeamDescriptions.xlsx"
    try:
        df = pd.read_excel(file_path)
        return True
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

def search_control(control):
    """Search for control in dataframe and return description"""
    try:
        matches = df[df.iloc[:, 1] == control]
        
        if not matches.empty:
            description = matches.iloc[0, 3]
            return description
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_ai_description(control):
    """Get AI description of the control"""
    try:
        API = os.getenv("AI_API_KEY")
        if not API:
            return "AI API key not found. Please check your environment variables."
        
        client = genai.Client(api_key=API)
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=f"Explain this FedRAMP control {control} in a short and simple way for a non technical user"
        )
        return response.text
    except Exception as e:
        return f"Error getting AI description: {e}"

def save_to_database(control, ai_description, weakness_description):
    """Save the search results to database"""
    try:
        db_file = "user_entries.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute("""CREATE TABLE IF NOT EXISTS requests (
                Control text,
                AI_Control_Description text,
                ProjectTeam_Weakness_Description text
                )""")
        
        # Insert data
        cursor.execute("INSERT INTO requests VALUES (?,?,?)", 
                      (control, ai_description, weakness_description))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

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
                                 error="AI API key not found. Please check your environment variables.")
        
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

@app.route('/search', methods=['POST'])
def search():
    """Handle search requests"""
    control = request.form.get('control')
    
    if not control:
        return redirect(url_for('index'))
    
    # Search for weakness description
    weakness_description = search_control(control)
    
    if weakness_description is None:
        return render_template('result.html', 
                             control=control,
                             error=f"The control {control} was not found in the file.")
    
    # Get AI description
    ai_description = get_ai_description(control)
    
    # Save to database
    save_to_database(control, ai_description, weakness_description)
    
    return render_template('result.html', 
                         control=control,
                         ai_description=ai_description,
                         weakness_description=weakness_description)

@app.route('/api/controls')
def get_controls():
    """API endpoint to get list of controls"""
    if df is None:
        load_data()
    
    if df is not None:
        controls_list = df.iloc[:, 1].unique().tolist()
        return jsonify(controls_list)
    else:
        return jsonify([])

@app.route('/history')
def history():
    """Show search history from database"""
    try:
        db_file = "user_entries.db"
        if not os.path.exists(db_file):
            return render_template('history.html', entries=[])
        
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM requests ORDER BY rowid DESC LIMIT 20")
        entries = cursor.fetchall()
        
        conn.close()
        
        return render_template('history.html', entries=entries)
    except Exception as e:
        return render_template('error.html', error=f"Database error: {e}")

if __name__ == '__main__':
    app.run(debug=True)