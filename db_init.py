import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234", # Update if necessary
    "database": "signin_db",
}

def setup_database():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Create Tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        item_id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        price DECIMAL(10,2) NOT NULL,
        date_posted DATE NOT NULL,
        seller VARCHAR(45) NOT NULL,
        FOREIGN KEY (seller) REFERENCES users(username) ON DELETE CASCADE
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        category_name VARCHAR(50) PRIMARY KEY
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS item_categories (
        item_id INT,
        category_name VARCHAR(50),
        PRIMARY KEY (item_id, category_name),
        FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE,
        FOREIGN KEY (category_name) REFERENCES categories(category_name) ON DELETE CASCADE
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        review_id INT AUTO_INCREMENT PRIMARY KEY,
        item_id INT NOT NULL,
        reviewer VARCHAR(45) NOT NULL,
        rating VARCHAR(10) NOT NULL,
        comment TEXT,
        review_date DATE NOT NULL,
        UNIQUE (item_id, reviewer), -- Enforces 1 review per item per user
        FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE,
        FOREIGN KEY (reviewer) REFERENCES users(username) ON DELETE CASCADE,
        CHECK (rating IN ('Excellent', 'Good', 'Fair', 'Poor'))
    )""")

    # Create Triggers to Enforce Business Rules
    cursor.execute("DROP TRIGGER IF EXISTS check_item_limit")
    cursor.execute("""
    CREATE TRIGGER check_item_limit BEFORE INSERT ON items
    FOR EACH ROW
    BEGIN
        DECLARE item_count INT;
        SELECT COUNT(*) INTO item_count FROM items WHERE seller = NEW.seller AND date_posted = NEW.date_posted;
        IF item_count >= 2 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'A user may post at most two items per calendar day.';
        END IF;
    END;""")

    cursor.execute("DROP TRIGGER IF EXISTS check_review_limit")
    cursor.execute("""
    CREATE TRIGGER check_review_limit BEFORE INSERT ON reviews
    FOR EACH ROW
    BEGIN
        DECLARE review_count INT;
        DECLARE item_seller VARCHAR(45);
        SELECT COUNT(*) INTO review_count FROM reviews WHERE reviewer = NEW.reviewer AND review_date = NEW.review_date;
        IF review_count >= 3 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'A user may submit at most three reviews per calendar day.';
        END IF;
        
        SELECT seller INTO item_seller FROM items WHERE item_id = NEW.item_id;
        IF item_seller = NEW.reviewer THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'A user cannot review their own item.';
        END IF;
    END;""")

    cursor.execute("DROP TRIGGER IF EXISTS prevent_review_update")
    cursor.execute("""
    CREATE TRIGGER prevent_review_update BEFORE UPDATE ON reviews
    FOR EACH ROW
    BEGIN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Once submitted, a review cannot be modified.';
    END;""")

    print("Phase 2 database tables and triggers successfully initialized!")
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    setup_database()