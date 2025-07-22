import duckdb
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import litellm
from jinja2 import Environment, FileSystemLoader
import json
import logging

# Configure logging for container environments
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Force Python to flush stdout immediately (important for containers)
sys.stdout.reconfigure(line_buffering=True)

def log_and_print(message, level="info", to_stderr=False):
    """Helper function to both log and print messages to avoid duplication"""
    # Log using the logging framework
    if level == "info":
        logger.info(message)
    elif level == "error":
        logger.error(message)
    elif level == "warning":
        logger.warning(message)
    
    # Print to console with flush for container compatibility
    output_stream = sys.stderr if to_stderr else sys.stdout
    print(message, file=output_stream, flush=True)

def call_litellm(messages, model="gpt-4-1", tools=None, tool_choice=None):
    """Helper function to call LiteLLM with consistent configuration"""
    return litellm.completion(
        model=f"{model}",
        messages=messages,
        api_base=f"https://litellm.prod-ai.riotgames.io/openai/deployments/{model}",
        api_key="sk-Gdvcor9sHOvqNvWce-CMAQ",
        tools=tools,
        tool_choice=tool_choice,
        custom_llm_provider="openai"
    )

# Configure LiteLLM for Riot Games endpoint
litellm.api_base = "https://litellm.prod-ai.riotgames.io/openai/deployments"
litellm.api_key = "sk-Gdvcor9sHOvqNvWce-CMAQ"
os.environ["OPENAI_API_KEY"] = "sk-Gdvcor9sHOvqNvWce-CMAQ"

app = Flask(__name__)
CORS(app)

DB_FILE = "thunderdome.duckdb"

# Initialize DuckDB connection (in-memory to avoid file locking issues)
conn = duckdb.connect(DB_FILE, read_only=False)

# Set up the environment to load templates from ./prompt directory
# env = Environment(loader=FileSystemLoader('/app/prompt'))
# sql_prompt_template = env.get_template('sql_generator_prompt_template.jinja')


def setup_database():
    """Initialize the database and load CSV data"""
    try:
        conn.execute(f"""
            CREATE OR REPLACE TABLE cloudflare_data AS
            SELECT * FROM read_csv_auto('../thunderdome_files/cloudflare/*.csv', header=True)
        """)
        conn.execute(f"""
            CREATE OR REPLACE TABLE akamai_data AS
            SELECT * FROM read_csv_auto('../thunderdome_files/akamai/*.csv', header=True)
        """)
        log_and_print("Database setup completed successfully")
    except Exception as e:
        log_and_print(f"Error setting up database: {e}", "error")

def execute_duckdb_query(sql_query):
    """Execute a SQL query on DuckDB and return results"""
    try:
        result = conn.execute(sql_query).fetchall()
        columns = [desc[0] for desc in conn.description]
        rows = [dict(zip(columns, row)) for row in result]
        return {
            "success": True,
            "data": rows,
            "columns": columns,
            "row_count": len(rows)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_database_schema():
    """Get the database schema for function calling"""
    try:
        tables = conn.execute("SHOW TABLES;").fetchall()
        schema_info = {}
        for table_name_tuple in tables:
            table_name = table_name_tuple[0]
            columns_df = conn.execute(f"DESCRIBE {table_name};").df()
            schema_info[table_name] = columns_df.to_dict('records')
        return schema_info
    except Exception as e:
        return {"error": str(e)}
    
def get_database_schema_pretty():
    """
    Connects directly to the DuckDB file to get the schema.
    This is the correct way to get context for the LLM.
    """
    log_and_print("Getting database schema locally...")
    schema_parts = []
    try:
        tables = conn.execute("SHOW TABLES;").fetchall()
        for table_name_tuple in tables:
            table_name = table_name_tuple[0]
            columns_df = conn.execute(f"DESCRIBE {table_name};").df()
            schema_parts.append(f"Table '{table_name}':\n{columns_df.to_string()}\n")
        log_and_print("✅ Schema received.")
        return "\n".join(schema_parts)
    except Exception as e:
        log_and_print(f"❌ Error getting local schema: {e}", "error", to_stderr=True)
        return "Could not retrieve schema."

def message_to_dict(message):
    """Convert LiteLLM message object to JSON-serializable dictionary"""
    if hasattr(message, 'model_dump'):
        # For newer LiteLLM versions
        return message.model_dump()
    elif hasattr(message, 'dict'):
        # For older versions
        return message.dict()
    else:
        # Fallback manual conversion
        result = {
            "role": getattr(message, 'role', 'assistant'),
            "content": getattr(message, 'content', None)
        }
        if hasattr(message, 'tool_calls') and message.tool_calls:
            result["tool_calls"] = []
            for tool_call in message.tool_calls:
                tool_call_dict = {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                }
                result["tool_calls"].append(tool_call_dict)
        return result

def query_litellm(prompt, model="gpt-4-1", use_tools=False):
    log_and_print(f"Sending prompt to model: {prompt}")

    # Define tools for function calling
    tools = [
        {
            "type": "function",
            "function": {
                "name": "execute_duckdb_query",
                "description": "Execute a SQL query on the DuckDB database containing AWS CUR (Cost and Usage Report) data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql_query": {
                            "type": "string",
                            "description": "The SQL query to execute on the database"
                        }
                    },
                    "required": ["sql_query"]
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "get_database_schema",
                "description": "Get the schema information for all tables in the database",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ]

    messages = [{"role": "user", "content": prompt}]

    try:
        # Make initial request with or without tools
        response = call_litellm(
            messages=messages,
            model=model,
            tools=tools if use_tools else None,
            tool_choice="auto" if use_tools else None
        )
        
        # Handle multiple rounds of function calls
        max_iterations = 5  # Prevent infinite loops
        iteration = 0
        
        # If tools are not being used, return immediately
        if not use_tools:
            message = response.choices[0].message
            return {
                "content": message.content,
                "conversation": messages + [message_to_dict(message)],
                "iterations": 0
            }
        
        while use_tools and iteration < max_iterations:
            iteration += 1
            message = response.choices[0].message
            
            # Check if there are tool calls to process
            if not (hasattr(message, 'tool_calls') and message.tool_calls):
                # No more tool calls, return the final message
                return {
                    "content": message.content,
                    "conversation": messages + [message_to_dict(message)],
                    "iterations": iteration
                }
            
            # Add the assistant's message with tool calls to the conversation
            messages.append(message_to_dict(message))
            log_and_print(f"🔄 Function calling iteration {iteration}")
            
            # Process each tool call
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                log_and_print(f"🔧 Calling function: {function_name} with args: {function_args}")
                
                if function_name == "execute_duckdb_query":
                    function_result = execute_duckdb_query(function_args["sql_query"])
                elif function_name == "get_database_schema":
                    function_result = get_database_schema()
                else:
                    function_result = {"error": f"Unknown function: {function_name}"}
                
                # Add function result to messages
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(function_result)
                })
            
            # Get response after function calls (might trigger more function calls)
            response = call_litellm(
                messages=messages,
                model=model,
                tools=tools,
                tool_choice="auto"
            )
        
        # If we exit the loop, return the final response
        final_message = response.choices[0].message
        if iteration >= max_iterations:
            log_and_print(f"⚠️ Maximum function calling iterations ({max_iterations}) reached", "warning")
        
        # Add the final message to conversation and return
        messages.append(message_to_dict(final_message))
        
        # Return both the final content and the full conversation trace
        return {
            "content": final_message.content,
            "conversation": messages,
            "iterations": iteration
        }
        
    except Exception as e:
        log_and_print(f"🔥 LLM failure: {e}", "error")
        return f"Connection Error: {e}"


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "duckdb-ai-service"})


@app.route('/ask-with-tools', methods=['POST'])
def ask_question_with_tools():
    """Ask a natural language question using function calling to directly query the database"""
    try:
        data = request.get_json()
        question = data.get('question', '')

        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # Enhanced prompt that encourages the model to use tools
        enhanced_prompt = f"""
You have access to a DuckDB database with several tables of CDN data. 
The user's question is: "{question}"

Please use the available tools to:
1. First, get the database schema to understand the available tables and columns
2. Then execute appropriate SQL queries with exec`ute_duckdb_query to answer the question
3. Provide a clear, comprehensive answer based on the data you retrieve

Question: {question}
"""
        
        # Use function calling
        ai_response = query_litellm(enhanced_prompt, use_tools=True)
        
        return jsonify({
            "success": True,
            "question": question,
            "ai_response": ai_response["content"] if isinstance(ai_response, dict) else ai_response,
            "conversation": ai_response.get("conversation", []) if isinstance(ai_response, dict) else [],
            "iterations": ai_response.get("iterations", 0) if isinstance(ai_response, dict) else 0
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test', methods=['GET'])
def test_litellm_connection():
    """Test connectivity to the LLM (e.g., GPT-4-1 via LiteLLM)"""
    try:
        response = query_litellm("Say hello!")
        content = response["content"] if isinstance(response, dict) else response
        return jsonify({
            "success": True,
            "llm_response": content
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/test-tools', methods=['GET'])
def test_function_calling():
    """Test function calling capabilities"""
    try:
        test_prompt = "What tables are available in the database? Please check the schema and tell me about the data structure."
        response = query_litellm(test_prompt, use_tools=True)
        return jsonify({
            "success": True,
            "llm_response": response["content"] if isinstance(response, dict) else response,
            "conversation": response.get("conversation", []) if isinstance(response, dict) else [],
            "iterations": response.get("iterations", 0) if isinstance(response, dict) else 0
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    log_and_print("🚀 Starting DuckDB AI Service...")
    
    setup_database()

    print(get_database_schema_pretty())

    log_and_print("🌟 Service ready - starting Flask app...")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
