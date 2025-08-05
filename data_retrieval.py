import sqlite3

def control_search(user_input):
    conn = sqlite3.connect("user_entries.db")
    cursor = conn.cursor()
    #Query the data
    cursor.execute(f"SELECT * FROM requests WHERE Control = '{user_input}'")
    table_list = cursor.fetchall()

    print(f"\tControl\tAI Control Description\tProjectTeam Weakness Description")
    for item in table_list:
        print(f"{item}\n")
    #commit our command
    conn.commit()
    #close our connection
    conn.close()

def print_all():
    conn = sqlite3.connect("user_entries.db")
    cursor = conn.cursor()
    #Query the data
    cursor.execute("SELECT rowid, * FROM requests")
    table_list = cursor.fetchall()

    print(f"\tControl\tAI Control Description\tProjectTeam Weakness Description")
    for item in table_list:
        print(f"{item}\n")
    #commit our command
    conn.commit()
    #close our connection
    conn.close()

yes_no = input("Would you like to find an entry for a certain control? (Y/N) ")
if yes_no == "Y":
    control_input = input("Which control would you like to see? ")
    control_search(control_input)
else:
    print("Below are all the user entries")
    print("-" * 30)
    print_all()