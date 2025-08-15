from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
from dotenv import load_dotenv
from google import genai
import sqlite3
import markdown

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

def get_controls_list():
    """Get list of available controls from dataframe"""
    if df is not None:
        return df.iloc[:, 1].unique().tolist()
    return []

def get_ai_description(control, yes_no):
    """Get AI description of the control"""
    try:
        API = os.getenv("AI_API_KEY")
        if not API:
            return "AI API key not found. Please check your environment variables."
        
        client = genai.Client(api_key=API)
        if yes_no == "Yes":
            contents = f"Explain this FedRAMP control {control} in a short and simple way for a non technical user.In a new paragraph, give possible remediation efforts for this control"
            print("Include Remediation Steps")
        else:
            contents = f"Explain this FedRAMP control {control} in a short and simple way for a non technical user"
            print("No Remediation Steps")
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents = contents
        )
        response = response.text
        parsed_response = markdown.markdown(response)
        return parsed_response
    except Exception as e:
        return f"Error getting AI description: {e}"

def save_to_database(control, ai_description):
    """Save the search results to database"""
    try:
        db_file = "user_entries.db"
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Create table if it doesn't exist - simplified structure
        cursor.execute("""CREATE TABLE IF NOT EXISTS requests (
                Control text,
                AI_Control_Description text
                )""")
        
        # Insert data
        cursor.execute("INSERT INTO requests VALUES (?,?,?)", 
                      (control, ai_description, "test"))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False

@app.route('/')
def index():
    """Main page"""
    if df is None:
        if not load_data():
            return render_template('error.html', 
                                 error="Could not load data file. Please check if ./Spreadsheet/ProjectTeamDescriptions.xlsx exists.")
    
    # Get list of controls for the dropdown
    controls_list = get_controls_list()
    
    return render_template('index.html', controls=controls_list)

@app.route('/search', methods=['POST'])
def search():
    """Handle search requests"""
    control = request.form.get('control')
    print(control)
    if not control:
        control = request.form.get('manual_control')
        print(f'manual: {control}')
    
    if control is None:
        return render_template('index.html', 
                             controls=get_controls_list(),
                             error="Please select or enter a control name")
    yes_no = request.form.get('remediation_steps')
    print(yes_no)

    # Get AI description
    ai_description = get_ai_description(control, yes_no)
    
    # Save to database
    save_to_database(control, ai_description)
    
    return render_template('index.html',
                         controls=get_controls_list(),
                         ai_response=ai_description,
                         searched_control=control)

if __name__ == '__main__':
    app.run(debug=True)