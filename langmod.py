import openai
import tkinter as tk
from tkinter import simpledialog
import psycopg2
import os

# Access GPT-4 API key from system environment variables
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Generate GUI and prompt user for input
def get_user_input(prompt):
    root = tk.Tk()
    root.withdraw() 

    root.geometry("1000x400")

    user_input = simpledialog.askstring("DatabAIsed", prompt)

    root.destroy()  # Close the main window
    return user_input

# Connect to the PostgreSQL database
def connect_to_database():
    db_params = {
        'dbname': 'ai_articles',
        'user': 'postgres',     
        'password': os.environ.get("psql_pass"), 
        'host': 'localhost'
    }
    return psycopg2.connect(**db_params)

# Generate an SQL statement using GPT-4
user_input = get_user_input("How would you like to query the database?")
updated_input = f"You will play the role of a database query bot. The database in question is titled 'ai_articles' and contains information pertaining to scholarly articles on AI from the preprint site arxiv. The database contains three tables titled 'paper_by_doi', 'paper_authors', and 'authors'. The paper_by_doi table acts as the primary table and contains the attributes Arxiv_ID (TEXT PRIMARY KEY), Title (TEXT) and Date (TEXT). The paper_authors table contains the attributes Arxiv_ID VARCHAR(255) REFERENCES Paper_by_DOI(Arxiv_ID), Author_ID INTEGER REFERENCES Authors(Author_ID), and PRIMARY KEY (Arxiv_ID, Author_ID). Lastly, the authors table contains the attributes Author_ID SERIAL PRIMARY KEY, and Author_Name TEXT UNIQUE. As the query bot, understand that users expect to find specific entries within this database without having to familiarize themselves with SQL logic. As such, it is your responsibility to convert their natural language queries into corresponding SQL statements. Date values within the date attribute of the paper_by_doi table take the following form (as an example): Submitted 12 October, 2023; originally announced October 2023. Because of this, queries regarding dates should check to see whether the date attribute contains the user-requested month, date, or year, as opposed to outright checking for equality. The same rule applies to names, as well. For example, if the user requests 'all articles with Johnson listed as a contributing author', you would not check for outright equality, and instead identify any articles where Johnson is stored as a contributing author. In your response, only include the command, as it will be plugged into the database for querying. Users should not be able to modify the database in any way. It is simply a tool for retrieval of academic AI articles. The natural language input provided by the user is: {user_input}"
message=[{"role": "user", "content": updated_input}]
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages = message,
    temperature=0.2,
    max_tokens=1000,
    frequency_penalty=0.0
)

output = response['choices'][0]['message']['content']

# Use this for debugging purposes
new_sql_file = "generated_queries.sql"
with open(new_sql_file, "w") as generated_file:
    generated_file.write(output)

# Execute the generated SQL statement on the database
try:
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute(output)
    # Fetch results in the event its a SELECT statement
    if output.strip().lower().startswith('select'):
        result = cursor.fetchall()
        for row in result:
            print(row)
    conn.commit()
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        cursor.close()
        conn.close()