import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root", # Update if necessary
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
    CREATE TABLE IF NOT EXISTS review (
        itemID INT NOT NULL,
        username VARCHAR(45) NOT NULL,
        rating VARCHAR(45) NOT NULL,
        comment VARCHAR(200) NOT NULL,
        date DATE NOT NULL,
        PRIMARY KEY (itemID, username),
        FOREIGN KEY (itemID) REFERENCES item(itemID) ON DELETE CASCADE,
        FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE,
        CHECK (rating IN ('Excellent', 'Good', 'Fair', 'Poor')),
        CHECK (CHAR_LENGTH(comment) > 0)
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
    CREATE TRIGGER check_review_limit BEFORE INSERT ON review
    FOR EACH ROW
    BEGIN
        DECLARE review_count INT;
        DECLARE item_owner VARCHAR(45);

        SELECT COUNT(*) INTO review_count
        FROM review
        WHERE username = NEW.username AND date = NEW.date;

        IF review_count >= 3 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'A user may submit at most three reviews per calendar day.';
        END IF;

        SELECT poster_username INTO item_owner
        FROM item
        WHERE itemID = NEW.itemID;

        IF item_owner = NEW.username THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'A user cannot review their own item.';
        END IF;
    END;""")

    cursor.execute("DROP TRIGGER IF EXISTS prevent_review_update")
    cursor.execute("""
    CREATE TRIGGER prevent_review_update BEFORE UPDATE ON review
    FOR EACH ROW
    BEGIN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Once submitted, a review cannot be modified.';
    END;""")

    cursor.execute("DROP TRIGGER IF EXISTS prevent_review_delete")
    cursor.execute("""
    CREATE TRIGGER prevent_review_delete BEFORE DELETE ON review
    FOR EACH ROW
    BEGIN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reviews cannot be deleted after submission.';
    END;""")

    print("Phase 2 database tables and triggers successfully initialized!")
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    setup_database()