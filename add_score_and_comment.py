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
    conn = sqlite3.connect('./database_and_logs/langflow.db')
    return conn


def add_score_and_comment_to_message(
    conn: Connection,
    message_id: str,
    score: float,
    comment: Optional[str] = None
) -> None:
    """
    Adds score and comment attributes to the message table if they do not exist.
    Args:
        conn (Connection): The database connection object.
        message_id (str): The message ID to update.
        score (float): The score to be added.
        comment (Optional[str]): An optional comment to be added.
    Returns:
        None
    """
    cursor = conn.cursor()

    # Check if score column exists
    cursor.execute("PRAGMA table_info(message)")
    columns = [info[1] for info in cursor.fetchall()]

    if 'score' not in columns:
        cursor.execute("ALTER TABLE message ADD COLUMN score REAL")

    if 'comment' not in columns:
        cursor.execute("ALTER TABLE message ADD COLUMN comment TEXT")

    # Update the message with score and comment
    if comment is not None:
        cursor.execute(
            """
            UPDATE message
            SET score = ?, comment = ?
            WHERE id = ?
            """,
            (score, comment, message_id)
        )
    else:
        cursor.execute(
            """
            UPDATE message
            SET score = ?
            WHERE id = ?
            """,
            (score, message_id)
        )

    conn.commit()


@app.post("/add_score_and_comment/")
def add_score_and_comment_endpoint(
    message_id: str,
    score: float,
    comment: Optional[str] = None
):
    try:
        conn = get_db_connection()
        add_score_and_comment_to_message(conn, message_id, score, comment)
        conn.close()
        return {
            "status": "success",
            "message_id": message_id,
            "score": score,
            "comment": comment
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_full_message(
    conn: Connection,
) -> None:
    """
    Retrieves full messages from the message table.
    Args:
        conn (Connection): The database connection object.
    Returns:
        None
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM message")
    messages = cursor.fetchall()
    return messages


@app.get("/get_full_message/")
def get_full_message_endpoint():
    try:
        conn = get_db_connection()
        messages = get_full_message(conn)
        conn.close()
        return {"status": "success", "messages": messages}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Thêm endpoint để kiểm tra server
@app.get("/")
def root():
    return {"message": "Score and Comment API is running", "status": "healthy"}


# Thêm endpoint để kiểm tra cấu trúc bảng message
@app.get("/table_info/")
def get_table_info():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(message)")
        columns = cursor.fetchall()
        conn.close()
        return {"status": "success", "table_structure": columns}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    # Chạy server trên tất cả interfaces (127.0.0.1) thay vì chỉ localhost
    uvicorn.run(app, host="127.0.0.1", port=8000)
