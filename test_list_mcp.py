#!/usr/bin/env python3
"""
List all MCP servers to debug configuration
"""
import sqlite3
import json

# Connect to the database
db_path = "backend/data/webui.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query all MCP servers
cursor.execute("""
    SELECT id, name, transport_type, command, url, meta 
    FROM mcp_servers
""")

print("Current MCP Servers:")
print("-" * 80)

for row in cursor.fetchall():
    id, name, transport_type, command, url, meta = row
    print(f"ID: {id}")
    print(f"Name: {name}")
    print(f"Transport: {transport_type}")
    print(f"Command: {command}")
    print(f"URL: {url}")
    print(f"Meta: {meta}")
    print("-" * 80)

conn.close()