"""
SQL Agent wrapper for multi-user functionality using LangGraph.
This module adapts the LangGraph SQL agent tutorial for multi-user scenarios.
"""
import os
from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass

# For now, let's create a simplified version that mimics LangGraph functionality
# In a real implementation, these would be imported from langgraph and langchain


@dataclass
class ChatMessage:
    """Simplified message structure."""
    role: str
    content: str


class SimpleSQLAgent:
    """
    Simplified SQL Agent that mimics LangGraph's SQL agent functionality.
    This is a basic implementation for demonstration purposes.
    In production, this would use the full LangGraph SQL agent.
    """
    
    def __init__(self, database_path: str, llm_api_key: Optional[str] = None):
        self.database_path = database_path
        self.llm_api_key = llm_api_key or os.getenv("OPENAI_API_KEY")
        self.conversation_history: List[ChatMessage] = []
        
        # Import database manager
        from database import DatabaseManager
        self.db_manager = DatabaseManager(database_path)
    
    def _list_tables(self) -> str:
        """List all tables in the database."""
        try:
            tables = self.db_manager.get_table_names()
            if not tables:
                return "No tables found in the database. You may need to upload some data first."
            return f"Available tables: {', '.join(tables)}"
        except Exception as e:
            return f"Error listing tables: {str(e)}"
    
    def _get_table_schema(self, table_names: List[str]) -> str:
        """Get schema information for specified tables."""
        try:
            schema_info = []
            for table in table_names:
                if table in self.db_manager.get_table_names():
                    schema = self.db_manager.get_table_schema(table)
                    schema_str = f"\nTable: {table}\n"
                    for col in schema:
                        schema_str += f"  - {col['column']} ({col['type']})\n"
                    schema_info.append(schema_str)
                else:
                    schema_info.append(f"\nTable '{table}' not found.")
            
            return "".join(schema_info)
        except Exception as e:
            return f"Error getting schema: {str(e)}"
    
    def _execute_sql_query(self, query: str) -> Dict[str, Any]:
        """Execute a SQL query and return results."""
        try:
            # Basic SQL injection protection
            query = query.strip()
            if not query:
                return {"error": "Empty query"}
            
            # Prevent dangerous operations
            dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
            query_upper = query.upper()
            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    return {"error": f"Operation '{keyword}' is not allowed for security reasons."}
            
            # Execute query
            results = self.db_manager.execute_query(query)
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "row_count": len(results)
            }
        
        except Exception as e:
            return {"error": f"Query execution error: {str(e)}"}
    
    def _generate_sql_query(self, user_question: str, available_tables: List[str]) -> str:
        """
        Generate SQL query based on user question.
        This is a simplified version - in production would use LLM.
        """
        
        # Simple keyword-based query generation for demonstration
        question_lower = user_question.lower()
        
        # Basic patterns for common queries
        if "tables" in question_lower or "what tables" in question_lower:
            return "SELECT name FROM sqlite_master WHERE type='table'"
        
        if "customers" in question_lower and "customers" in available_tables:
            if "count" in question_lower or "how many" in question_lower:
                return "SELECT COUNT(*) as customer_count FROM customers"
            elif "top" in question_lower or "best" in question_lower:
                return "SELECT * FROM customers LIMIT 5"
            else:
                return "SELECT * FROM customers LIMIT 10"
        
        if "orders" in question_lower and "orders" in available_tables:
            if "total" in question_lower or "sum" in question_lower:
                return "SELECT SUM(price * quantity) as total_revenue FROM orders"
            elif "recent" in question_lower or "latest" in question_lower:
                return "SELECT * FROM orders ORDER BY order_date DESC LIMIT 5"
            else:
                return "SELECT * FROM orders LIMIT 10"
        
        if "revenue" in question_lower or "sales" in question_lower:
            if "orders" in available_tables:
                return "SELECT product, SUM(price * quantity) as revenue FROM orders GROUP BY product ORDER BY revenue DESC"
        
        if available_tables:
            # Default: show sample data from first table
            return f"SELECT * FROM {available_tables[0]} LIMIT 5"
        
        return "SELECT 'No tables available' as message"
    
    def _format_query_results(self, results: List[Dict[str, Any]]) -> str:
        """Format query results for display."""
        if not results:
            return "No results found."
        
        if len(results) == 1 and len(results[0]) == 1:
            # Single value result
            value = list(results[0].values())[0]
            return f"Result: {value}"
        
        # Table format for multiple results
        if len(results) <= 10:  # Show full results for small datasets
            formatted = []
            if results:
                # Header
                headers = list(results[0].keys())
                formatted.append(" | ".join(headers))
                formatted.append("-" * len(" | ".join(headers)))
                
                # Rows
                for row in results:
                    formatted.append(" | ".join(str(row[col]) for col in headers))
            
            return "\n".join(formatted)
        else:
            # Summary for large datasets
            return f"Found {len(results)} results. Showing first 5:\n" + self._format_query_results(results[:5])
    
    def process_user_query(self, user_input: str) -> Dict[str, Any]:
        """
        Process a user query and return response.
        This simulates the LangGraph SQL agent workflow.
        """
        
        try:
            # Step 1: List available tables
            available_tables = self.db_manager.get_table_names()
            
            # Step 2: Generate SQL query based on user input
            sql_query = self._generate_sql_query(user_input, available_tables)
            
            # Step 3: Execute the query
            query_result = self._execute_sql_query(sql_query)
            
            if "error" in query_result:
                return {
                    "response": f"I encountered an error: {query_result['error']}",
                    "error": query_result["error"]
                }
            
            # Step 4: Format the response
            formatted_results = self._format_query_results(query_result["results"])
            
            # Generate natural language response
            if "tables" in user_input.lower():
                response = f"Here are the available tables in your database:\n{formatted_results}"
            elif query_result["row_count"] == 0:
                response = "I found no results for your query."
            else:
                response = f"Based on your question '{user_input}', here's what I found:\n\n{formatted_results}"
            
            return {
                "response": response,
                "query_executed": sql_query,
                "results": query_result["results"],
                "row_count": query_result["row_count"]
            }
        
        except Exception as e:
            return {
                "response": f"I encountered an unexpected error: {str(e)}",
                "error": str(e)
            }
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the current database."""
        try:
            schema = self.db_manager.get_database_schema()
            table_info = {}
            
            for table in schema.tables:
                preview = self.db_manager.get_table_preview(table, limit=3)
                table_info[table] = {
                    "columns": [col["column"] for col in schema.table_schemas[table]],
                    "row_count": len(self.db_manager.execute_query(f"SELECT COUNT(*) as count FROM {table}")),
                    "sample_data": preview
                }
            
            return {
                "tables": schema.tables,
                "table_info": table_info
            }
        
        except Exception as e:
            return {"error": str(e)}