#!/usr/bin/env node
/**
 * Example MCP Server for Open WebUI
 * 
 * This creates a simple MCP server that can be connected via stdio transport
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';

// Create the MCP server
const server = new Server(
  {
    name: 'example-mcp-server',
    version: '0.1.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define a simple hello world tool
server.setRequestHandler('tools/list', async () => {
  return {
    tools: [
      {
        name: 'hello_world',
        description: 'Says hello to someone',
        inputSchema: {
          type: 'object',
          properties: {
            name: {
              type: 'string',
              description: 'Name of the person to greet'
            }
          },
          required: ['name']
        }
      },
      {
        name: 'add_numbers',
        description: 'Adds two numbers together',
        inputSchema: {
          type: 'object',
          properties: {
            a: {
              type: 'number',
              description: 'First number'
            },
            b: {
              type: 'number',
              description: 'Second number'
            }
          },
          required: ['a', 'b']
        }
      },
      {
        name: 'get_current_time',
        description: 'Gets the current time',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      }
    ]
  };
});

// Handle tool calls
server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case 'hello_world':
      return {
        content: [
          {
            type: 'text',
            text: `Hello, ${args.name}! This is a message from your local MCP server.`
          }
        ]
      };
    
    case 'add_numbers':
      const result = args.a + args.b;
      return {
        content: [
          {
            type: 'text',
            text: `The sum of ${args.a} and ${args.b} is ${result}`
          }
        ]
      };
    
    case 'get_current_time':
      return {
        content: [
          {
            type: 'text',
            text: `Current time: ${new Date().toLocaleString()}`
          }
        ]
      };
    
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Example MCP server running...');
}

main().catch(console.error);