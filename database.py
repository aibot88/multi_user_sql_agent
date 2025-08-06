"""
Database management utilities for the multi-user SQL agent application.
"""
import sqlite3
import pandas as pd
import os
from typing import List, Dict, Any, Optional
from models import DatabaseSchema


class DatabaseManager:
    """Manages user databases and data operations."""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Ensure the database file and directory exist."""
        os.makedirs(os.path.dirname(self.database_path), exist_ok=True)
        
        # Create database file if it doesn't exist
        if not os.path.exists(self.database_path):
            with sqlite3.connect(self.database_path) as conn:
                conn.execute("SELECT 1")  # Simple query to create the file
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.row_factory = sqlite3.Row  # Enable column access by name
                cursor = conn.execute(query)
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                return [dict(row) for row in rows]
        
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
    
    def get_table_names(self) -> List[str]:
        """Get list of all table names in the database."""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        results = self.execute_query(query)
        return [row['name'] for row in results]
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, str]]:
        """Get schema information for a specific table."""
        query = f"PRAGMA table_info({table_name})"
        results = self.execute_query(query)
        
        schema = []
        for row in results:
            schema.append({
                'column': row['name'],
                'type': row['type'],
                'nullable': 'YES' if not row['notnull'] else 'NO',
                'primary_key': 'YES' if row['pk'] else 'NO'
            })
        
        return schema
    
    def get_database_schema(self) -> DatabaseSchema:
        """Get complete database schema."""
        tables = self.get_table_names()
        table_schemas = {}
        
        for table in tables:
            table_schemas[table] = self.get_table_schema(table)
        
        return DatabaseSchema(tables=tables, table_schemas=table_schemas)
    
    def create_table_from_dataframe(self, df: pd.DataFrame, table_name: str, if_exists: str = 'replace') -> None:
        """Create a table from a pandas DataFrame."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                df.to_sql(table_name, conn, if_exists=if_exists, index=False)
        except Exception as e:
            raise Exception(f"Error creating table {table_name}: {str(e)}")
    
    def upload_csv_data(self, csv_file_path: str, table_name: Optional[str] = None) -> List[str]:
        """Upload CSV data to the database."""
        try:
            # Read CSV file
            df = pd.read_csv(csv_file_path)
            
            # Use filename as table name if not provided
            if table_name is None:
                table_name = os.path.splitext(os.path.basename(csv_file_path))[0]
            
            # Clean table name (remove special characters)
            table_name = "".join(c for c in table_name if c.isalnum() or c == '_')
            
            # Create table
            self.create_table_from_dataframe(df, table_name)
            
            return [table_name]
        
        except Exception as e:
            raise Exception(f"Error uploading CSV data: {str(e)}")
    
    def create_sample_data(self) -> List[str]:
        """Create sample data for demonstration."""
        try:
            # Sample customers data
            customers_data = {
                'customer_id': [1, 2, 3, 4, 5],
                'name': ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Eve Brown'],
                'email': ['alice@email.com', 'bob@email.com', 'carol@email.com', 'david@email.com', 'eve@email.com'],
                'city': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
            }
            
            # Sample orders data
            orders_data = {
                'order_id': [101, 102, 103, 104, 105, 106, 107, 108],
                'customer_id': [1, 2, 1, 3, 4, 2, 5, 3],
                'product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones', 'Webcam', 'Tablet', 'Printer'],
                'quantity': [1, 2, 1, 1, 1, 1, 1, 1],
                'price': [999.99, 29.99, 79.99, 299.99, 149.99, 89.99, 399.99, 199.99],
                'order_date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19', '2024-01-20', '2024-01-21', '2024-01-22']
            }
            
            # Create DataFrames
            customers_df = pd.DataFrame(customers_data)
            orders_df = pd.DataFrame(orders_data)
            
            # Create tables
            self.create_table_from_dataframe(customers_df, 'customers')
            self.create_table_from_dataframe(orders_df, 'orders')
            
            return ['customers', 'orders']
        
        except Exception as e:
            raise Exception(f"Error creating sample data: {str(e)}")
    
    def get_table_preview(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get a preview of table data."""
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.execute_query(query)