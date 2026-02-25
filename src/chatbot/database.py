"""
Database module: provides safe SQL query execution for the chatbot.
- Validates SQL (blocks INSERT, UPDATE, DELETE, DROP).
- Executes SELECT queries against sample.db.
- Returns results as formatted strings or error messages.
"""
import sqlite3
import re
from typing import List, Tuple, Optional


DB_PATH = "data/sample.db"


def execute_sql_query(sql_query: str) -> str:
    """
    Execute a SQL query against the sample database.
    
    Args:
        sql_query: The SQL query string to execute.
        
    Returns:
        A formatted string with the query result or an error message.
        
    Raises:
        ValueError: If the SQL is invalid (e.g., destructive operations).
    """
    # Validate SQL: only allow SELECT
    sql_upper = sql_query.strip().upper()
    
    # Block dangerous operations
    if any(kw in sql_upper for kw in ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE"]):
        return "Error: Only SELECT queries are allowed. Destructive operations are blocked."
    
    if not sql_upper.startswith("SELECT"):
        return "Error: Only SELECT queries are allowed."
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Return rows as dicts
        cursor = conn.cursor()
        
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        conn.close()
        
        # Format result
        if not rows:
            return "Query returned no results."
        
        # Convert rows to list of dicts for easy formatting
        result_list = [dict(row) for row in rows]
        
        # If only one row and one column (e.g., COUNT(*)), return just the value
        if len(result_list) == 1 and len(result_list[0]) == 1:
            col_name = list(result_list[0].keys())[0]
            return str(result_list[0][col_name])
        
        # Format as readable table/list
        return _format_result(result_list)
    
    except sqlite3.Error as e:
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"Error executing query: {str(e)}"


def _format_result(rows: List[dict]) -> str:
    """Format query results as a readable string."""
    if not rows:
        return "No results."
    
    # Get column names from first row
    cols = list(rows[0].keys())
    
    # Build formatted output
    lines = []
    lines.append(", ".join(cols))  # Header
    for row in rows:
        values = [str(row[col]) for col in cols]
        lines.append(", ".join(values))
    
    return "\n".join(lines)


def get_db_schema() -> str:
    """
    Return the database schema as a formatted string.
    Useful for the system prompt to inform the LLM about available tables.
    """
    schema = """
Database Schema:

Table: customers
- id (INTEGER PRIMARY KEY)
- name (TEXT)
- email (TEXT)
- country (TEXT)
- signup_date (TEXT, format: YYYY-MM-DD)

Table: orders
- id (INTEGER PRIMARY KEY)
- customer_id (INTEGER, foreign key to customers.id)
- amount (REAL, in USD)
- order_date (TEXT, format: YYYY-MM-DD)
- status (TEXT, e.g., 'completed', 'pending')

Sample Queries:
- How many customers are there? → SELECT COUNT(*) FROM customers
- Which customers are from the UK? → SELECT name, email FROM customers WHERE country='UK'
- What is the total revenue from all orders? → SELECT SUM(amount) FROM orders
- Which customers have pending orders? → SELECT DISTINCT c.name FROM customers c JOIN orders o ON c.id=o.customer_id WHERE o.status='pending'
"""
    return schema.strip()
