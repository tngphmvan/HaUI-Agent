from sqlite3 import Connection
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Thêm CORS middleware để cho phép request từ tất cả địa chỉ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả origins
    allow_credentials=True,
    # Cho phép tất cả HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_methods=["*"],
    allow_headers=["*"],  # Cho phép tất cả headers
)


def get_db_connection() -> Connection:
    import sqlite3
    conn = sqlite3.connect('./database_and_logs/langflow.db', timeout=30.0)
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    # Set WAL mode for better concurrency
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def create_comment_table(conn: Connection) -> None:
    """
    Creates the comment table if it doesn't exist.
    """
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT NOT NULL,
            score REAL NOT NULL CHECK (score >= 0 AND score <= 100),
            comment_text TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (message_id) REFERENCES message (id) ON DELETE CASCADE
        )
    """)

    # Create index for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_comment_message_id ON comment(message_id)
    """)

    conn.commit()


def add_score_and_comment_to_message(
    conn: Connection,
    message_id: str,
    score: float,
    comment: Optional[str] = None
) -> None:
    """
    Adds score and comment to the comment table linked to a message.
    Args:
        conn (Connection): The database connection object.
        message_id (str): The message ID to link the comment to.
        score (float): The score to be added (1-5).
        comment (Optional[str]): An optional comment text.
    Returns:
        None
    """
    cursor = conn.cursor()

    # Ensure comment table exists
    create_comment_table(conn)

    # Check if message exists
    cursor.execute("SELECT id FROM message WHERE id = ?", (message_id,))
    if not cursor.fetchone():
        raise ValueError(f"Message with id {message_id} does not exist")

    # Check if comment already exists for this message
    cursor.execute(
        "SELECT id FROM comment WHERE message_id = ?", (message_id,))
    existing_comment = cursor.fetchone()

    if existing_comment:
        # Update existing comment
        cursor.execute(
            """
            UPDATE comment
            SET score = ?, comment_text = ?, updated_at = CURRENT_TIMESTAMP
            WHERE message_id = ?
            """,
            (score, comment, message_id)
        )
    else:
        # Insert new comment
        cursor.execute(
            """
            INSERT INTO comment (message_id, score, comment_text)
            VALUES (?, ?, ?)
            """,
            (message_id, score, comment)
        )

    conn.commit()


@app.post("/add_score_and_comment/")
def add_score_and_comment_endpoint(
    message_id: str,
    score: float,
    comment: Optional[str] = None
):
    conn = None
    try:
        conn = get_db_connection()
        add_score_and_comment_to_message(conn, message_id, score, comment)
        return {
            "status": "success",
            "message_id": message_id,
            "score": score,
            "comment": comment
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            conn.close()


def get_full_message_with_comments(conn: Connection):
    """
    Retrieves all messages with their associated comments and scores.
    Args:
        conn (Connection): The database connection object.
    Returns:
        List of messages with comments
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            m.*,
            c.score,
            c.comment_text,
            c.created_at as comment_created_at,
            c.updated_at as comment_updated_at
        FROM message m
        LEFT JOIN comment c ON m.id = c.message_id
        ORDER BY m.timestamp DESC
    """)

    # Get column names
    columns = [description[0] for description in cursor.description]

    # Convert to list of dictionaries
    messages = []
    for row in cursor.fetchall():
        message_dict = dict(zip(columns, row))
        messages.append(message_dict)

    return messages


def get_full_message(conn: Connection):
    """
    Retrieves full messages from the message table.
    Args:
        conn (Connection): The database connection object.
    Returns:
        List of messages
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM message")
    messages = cursor.fetchall()
    return messages


def get_message_comments(conn: Connection, message_id: str):
    """
    Retrieves comments for a specific message.
    Args:
        conn (Connection): The database connection object.
        message_id (str): The message ID to get comments for.
    Returns:
        Comment data for the message
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM comment WHERE message_id = ?
    """, (message_id,))

    columns = [description[0] for description in cursor.description]
    comment_data = cursor.fetchone()

    if comment_data:
        return dict(zip(columns, comment_data))
    return None


@app.get("/get_full_message/")
def get_full_message_endpoint():
    conn = None
    try:
        conn = get_db_connection()
        messages = get_full_message(conn)
        return {"status": "success", "messages": messages}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            conn.close()


@app.get("/get_messages_with_comments/")
def get_messages_with_comments_endpoint():
    """Get all messages with their associated comments and scores"""
    conn = None
    try:
        conn = get_db_connection()
        messages = get_full_message_with_comments(conn)
        return {"status": "success", "messages": messages}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            conn.close()


@app.get("/get_message_comment/{message_id}")
def get_message_comment_endpoint(message_id: str):
    """Get comment and score for a specific message"""
    conn = None
    try:
        conn = get_db_connection()
        comment = get_message_comments(conn, message_id)

        if comment:
            return {"status": "success", "comment": comment}
        else:
            return {"status": "success", "comment": None, "message": "No comment found for this message"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            conn.close()


# Thêm endpoint để kiểm tra server
@app.get("/")
def root():
    return {"message": "Score and Comment API is running", "status": "healthy"}


@app.get("/health_check/")
def health_check():
    """Check database connectivity and server health"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        return {
            "status": "healthy",
            "database": "connected",
            "message": "Database connection successful"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "error",
            "message": f"Database connection failed: {str(e)}"
        }
    finally:
        if conn:
            conn.close()


# Thêm endpoint để kiểm tra cấu trúc bảng message và comment
@app.get("/table_info/")
def get_table_info():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get message table structure
        cursor.execute("PRAGMA table_info(message)")
        message_columns = cursor.fetchall()

        # Create comment table if not exists and get its structure
        create_comment_table(conn)
        cursor.execute("PRAGMA table_info(comment)")
        comment_columns = cursor.fetchall()

        return {
            "status": "success",
            "message_table": message_columns,
            "comment_table": comment_columns
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            conn.close()


@app.get("/comment_statistics/")
def get_comment_statistics():
    """Get statistics about comments and scores"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Total comments
        cursor.execute("SELECT COUNT(*) FROM comment")
        total_comments = cursor.fetchone()[0]

        # Average score
        cursor.execute("SELECT AVG(score) FROM comment")
        avg_score_result = cursor.fetchone()[0]
        avg_score = round(avg_score_result, 2) if avg_score_result else 0

        # Score distribution
        cursor.execute("""
            SELECT score, COUNT(*) as count 
            FROM comment 
            GROUP BY score 
            ORDER BY score
        """)
        score_distribution = dict(cursor.fetchall())

        # Messages with comments vs without
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT m.id) as total_messages,
                COUNT(DISTINCT c.message_id) as messages_with_comments
            FROM message m
            LEFT JOIN comment c ON m.id = c.message_id
        """)
        message_stats = cursor.fetchone()
        total_messages, messages_with_comments = message_stats
        messages_without_comments = total_messages - messages_with_comments

        return {
            "status": "success",
            "statistics": {
                "total_comments": total_comments,
                "average_score": avg_score,
                "score_distribution": score_distribution,
                "total_messages": total_messages,
                "messages_with_comments": messages_with_comments,
                "messages_without_comments": messages_without_comments,
                "comment_coverage_percentage": round((messages_with_comments / total_messages * 100), 2) if total_messages > 0 else 0
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    import uvicorn
    # Chạy server trên tất cả interfaces (0.0.0.0) để cho phép truy cập từ mọi máy
    uvicorn.run(app, host="0.0.0.0", port=8000)
