import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root", 
        database="gambler_db"
    )

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gamblers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            stake DECIMAL(10,2),
            initial_stake DECIMAL(10,2),
            win_threshold DECIMAL(10,2),
            loss_threshold DECIMAL(10,2),
            total_bets INT DEFAULT 0,
            wins INT DEFAULT 0,
            losses INT DEFAULT 0,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    print("Database initialized.")