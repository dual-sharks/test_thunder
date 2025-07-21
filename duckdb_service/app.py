import duckdb
import pandas as pd
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# Initialize DuckDB connection (in-memory to avoid file locking issues)
conn = duckdb.connect(':memory:')

def setup_database():
    """Initialize the database and load CSV data"""
    try:
        # Create table and load CSV data
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions AS 
            SELECT * FROM read_csv_auto('/app/data/sample_data.csv')
        """)
        print("Database setup completed successfully")
    except Exception as e:
        print(f"Error setting up database: {e}")

def query_ollama(prompt, model="llama3.1"):
    """Send query to Ollama service"""
    try:
        ollama_url = os.getenv('OLLAMA_URL', 'http://ollama:11434')
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        if response.status_code == 200:
            return response.json().get('response', '')
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error connecting to Ollama: {e}"

def generate_sql_from_question(question):
    """Generate SQL query from natural language question using AI"""
    schema_info = """
    Table: transactions
    Columns:
    - transaction_id (INTEGER): Unique identifier for each transaction
    - date (DATE): Transaction date in YYYY-MM-DD format
    - amount (DECIMAL): Transaction amount (positive for income, negative for expenses)
    - category (VARCHAR): Category of the transaction (salary, food, utilities, etc.)
    - description (VARCHAR): Description of the transaction
    - merchant (VARCHAR): Merchant or company name
    - account_type (VARCHAR): Type of account (checking, credit, etc.)
    
    Sample data:
    transaction_id | date       | amount  | category | description | merchant | account_type
    1             | 2025-01-15 | 1250.00 | salary   | Monthly salary payment | ABC Company | checking
    2             | 2025-01-16 | -45.67  | food     | Grocery shopping | SuperMart | checking
    """
    
    prompt = f"""
    You are a SQL expert. Given this database schema for financial transactions:
    
    {schema_info}
    
    Generate a DuckDB SQL query to answer this question: "{question}"
    
    Rules:
    1. Only return the SQL query, no explanation
    2. Use proper DuckDB syntax
    3. Be precise with column names and data types
    4. Use appropriate aggregations and filters
    5. Return only the SQL query between triple backticks
    
    Question: {question}
    """
    
    response = query_ollama(prompt)
    
    # Extract SQL from response
    if "```sql" in response:
        sql = response.split("```sql")[1].split("```")[0].strip()
    elif "```" in response:
        sql = response.split("```")[1].split("```")[0].strip()
    else:
        sql = response.strip()
    
    return sql

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "duckdb-ai-service"})

@app.route('/query', methods=['POST'])
def execute_query():
    """Execute SQL query on the database"""
    try:
        data = request.get_json()
        sql_query = data.get('sql', '')
        
        if not sql_query:
            return jsonify({"error": "No SQL query provided"}), 400
        
        result = conn.execute(sql_query).fetchall()
        columns = [desc[0] for desc in conn.description]
        
        # Convert to list of dictionaries
        rows = [dict(zip(columns, row)) for row in result]
        
        return jsonify({
            "success": True,
            "data": rows,
            "columns": columns,
            "row_count": len(rows)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    """Ask a natural language question about the financial data"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # Generate SQL from natural language
        sql_query = generate_sql_from_question(question)
        
        # Execute the generated SQL
        result = conn.execute(sql_query).fetchall()
        columns = [desc[0] for desc in conn.description]
        rows = [dict(zip(columns, row)) for row in result]
        
        # Generate natural language response
        response_prompt = f"""
        Based on this SQL query result for the question "{question}":
        
        SQL Query: {sql_query}
        Results: {rows}
        
        Provide a clear, natural language answer to the original question. Be specific with numbers and insights.
        """
        
        ai_response = query_ollama(response_prompt)
        
        return jsonify({
            "success": True,
            "question": question,
            "sql_query": sql_query,
            "data": rows,
            "ai_response": ai_response,
            "row_count": len(rows)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/summary', methods=['GET'])
def get_summary():
    """Get a summary of the financial data"""
    try:
        # Get basic statistics
        summary_query = """
        SELECT 
            COUNT(*) as total_transactions,
            SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as total_expenses,
            SUM(amount) as net_amount,
            COUNT(DISTINCT category) as unique_categories,
            MIN(date) as earliest_date,
            MAX(date) as latest_date
        FROM transactions
        """
        
        result = conn.execute(summary_query).fetchone()
        
        summary = {
            "total_transactions": result[0],
            "total_income": float(result[1]),
            "total_expenses": float(result[2]),
            "net_amount": float(result[3]),
            "unique_categories": result[4],
            "date_range": f"{result[5]} to {result[6]}"
        }
        
        return jsonify({"success": True, "summary": summary})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/categories', methods=['GET'])
def get_categories():
    """Get spending by category"""
    try:
        category_query = """
        SELECT 
            category,
            COUNT(*) as transaction_count,
            SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as total_spent,
            SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as total_earned,
            AVG(amount) as avg_amount
        FROM transactions
        GROUP BY category
        ORDER BY total_spent DESC
        """
        
        result = conn.execute(category_query).fetchall()
        columns = [desc[0] for desc in conn.description]
        rows = [dict(zip(columns, row)) for row in result]
        
        return jsonify({"success": True, "categories": rows})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    setup_database()
    app.run(host='0.0.0.0', port=5000, debug=True)
