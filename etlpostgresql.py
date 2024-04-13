import psycopg2

# Database URL
url = "postgres://analyzar_db_e8ou_user:oNSbiWJurpryUxZNIjjorWwUJPq4I0e4@dpg-co7ek8cf7o1s73cm96rg-a.singapore-postgres.render.com/analyzar_db_e8ou"

# Establish a connection to the PostgreSQL database
try:
    conn = psycopg2.connect(url)
    print("Connected to database successfully!")
except psycopg2.Error as e:
    print("Unable to connect to the database:", e)
    exit(1)

# Create a cursor object to execute SQL queries
cur = conn.cursor()

# Execute the query to create the 'userdata' table
try:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_details (
            id SERIAL PRIMARY KEY,
            Name VARCHAR(50),
            Email VARCHAR(100),
            Unique_Code VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Table 'user_details' created successfully!")
except psycopg2.Error as e:
    print("Error creating table:", e)
    conn.rollback()

# Insert some dummy entries into the 'userdata' table
try:
    cur.execute("""
        INSERT INTO user_details (Name, Email, Unique_Code)
        VALUES 
        ('user1', 'user1@example.com', 'tbgf454'),
        ('user2', 'user2@example.com', '54t5t4ref'),
        ('user3', 'user3@example.com', 't54grfdvdf')
    """)
    print("Dummy entries inserted successfully!")
    conn.commit()
except psycopg2.Error as e:
    print("Error inserting data:", e)
    conn.rollback()

# Execute the query to select entire table called 'userdata'
try:
    cur.execute("SELECT * FROM user_details")
    rows = cur.fetchall()
    
    # Display the results
    for row in rows:
        print(row)
        
except psycopg2.Error as e:
    print("Error executing query:", e)

# Close cursor and connection
cur.close()
conn.close()
