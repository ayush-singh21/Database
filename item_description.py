import pandas as pd
import os
from dotenv import load_dotenv
from google import genai
import sqlite3

def search():

    try:

        matches = df[df.iloc[:, 1] == control] #checks to see if the control entered by user has a match in the dataframe

        if not matches.empty:
            description = matches.iloc[0,3]
            print(f"\nWeakness Description of {control} for ProjectTeam: {description}")
        else:
            print(f"The control {control} was not found in the file.")
    except Exception as e:
        print(f"An error occured {e}. Please try again.")
    return(description)

def list():
    options = input("Would you like a list of controls you can ask for? (Y/N) ")
    while options:
        if options == "Y":
            for value in df["Controls"]:
                print(value)
            break
        elif options == "N":
            break
        else:
            options = input("Please enter Y or N: ")

def ai_description():
    load_dotenv()
    API = os.getenv("AI_API_KEY")
    #print(API)

    client = genai.Client(api_key=API)


    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=f"Explain this FedRAMP control {control} in a short and simple way for a non technical user"
    )
    print(f"\nBelow is a short description of control {control}\n{response.text}")
    return response.text

def database():
    db_file = "user_entries.db"
    #connect to database
    conn = sqlite3.connect(db_file)
    #create a cursor
    cursor = conn.cursor()

    if not os.path.exists(db_file):

        #create a table
        cursor.execute("""CREATE TABLE requests (
                Control text,
                AI_Control_Description text,
                ProjectTeam_Weakness_Description text
                )""")
    
    #adding rows into table
    row = [(control, descrip, weakness)]

    #Executes the data into the database
    cursor.executemany("INSERT INTO requests VALUES (?,?,?)", row)

    conn.commit()
    conn.close()




if __name__ == "__main__":

    file_path = "./Spreadsheet/ProjectTeamDescriptions.xlsx"

    df = pd.read_excel(file_path) #creates dataframe for the data from the excel file
   
    list()
    control = input("\nEnter the control you would like the weakness description for: ") #gets the control from the user
    descrip = ai_description()
    weakness = search()
    database()



# from flask import Flask
# import sqlite3

# app = Flask(__name__)
# @app.route("/")

# def index():
#     return("Hello world!")

# app.run(debug=True)