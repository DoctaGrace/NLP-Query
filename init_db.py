import psycopg2
from scrape import scrape_arxiv_articles  # Ensure this function returns a list of articles with their associated authors


def initialize_database_and_scrape_articles():
    # Database connection parameters
    db_params = {
        'dbname': 'ai_articles',
        'user': 'postgres',
        'password': 'redacted',
        'host': 'localhost'
    }

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    # SQL statements to create tables
    create_table_statements = [
        """
        CREATE TABLE IF NOT EXISTS Paper_by_DOI (
            Arxiv_ID TEXT PRIMARY KEY,
            Title TEXT,
            Date TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Authors (
            Author_ID SERIAL PRIMARY KEY,
            Author_Name TEXT UNIQUE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Paper_Authors (
            Arxiv_ID VARCHAR(255) REFERENCES Paper_by_DOI(Arxiv_ID),
            Author_ID INTEGER REFERENCES Authors(Author_ID),
            PRIMARY KEY (Arxiv_ID, Author_ID)
        )
        """
    ]

    # Execute each SQL statement to create tables
    for statement in create_table_statements:
        cursor.execute(statement)

    # Commit the changes to create the tables
    conn.commit()

    # Call the scrape function to get articles
    articles = scrape_arxiv_articles()

    # Insert scraped data into the database
    for article in articles:
        # Insert the paper information
        cursor.execute(
            "INSERT INTO Paper_by_DOI (Arxiv_ID, Title, Date) VALUES (%s, %s, %s) ON CONFLICT (Arxiv_ID) DO NOTHING",
            (article.id, article.title, article.date)
        )

        # Insert authors and link them to the paper
        for author_name in article.authors:
            # Insert author if not exists and get the Author_ID
            cursor.execute(
                "INSERT INTO Authors (Author_Name) VALUES (%s) ON CONFLICT (Author_Name) DO NOTHING",
                (author_name,)
            )
            # Get the Author_ID of the inserted or existing author
            cursor.execute(
                "SELECT Author_ID FROM Authors WHERE Author_Name = %s",
                (author_name,)
            )
            author_id = cursor.fetchone()[0]

            # Link paper and author
            cursor.execute(
                "INSERT INTO Paper_Authors (Arxiv_ID, Author_ID) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (article.id, author_id)
            )

    # Commit the changes to insert articles and authors
    conn.commit()

    # Close the cursor and the connection
    cursor.close()
    conn.close()

    print("Database initialized and articles inserted successfully.")

# Run the function
initialize_database_and_scrape_articles()
