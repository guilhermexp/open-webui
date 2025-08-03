import { MCP_API_BASE_URL, WEBUI_API_BASE_URL } from '$lib/constants';

export interface MCPServerForm {
	name: string;
	transport_type: 'stdio' | 'http' | 'websocket';
	command?: string;
	url?: string;
	args?: string[];
	env?: Record<string, string>;
	enabled: boolean;
	meta?: Record<string, any>;
}

export interface MCPServer {
	id: string;
	user_id: string;
	name: string;
	transport_type: 'stdio' | 'http' | 'websocket';
	command?: string;
	url?: string;
	args: string[];
	env: Record<string, string>;
	enabled: boolean;
	meta: Record<string, any>;
	created_at: number;
	updated_at: number;
}

export interface MCPTool {
	id: string;
	server_id: string;
	tool_name: string;
	description?: string;
	parameters: Record<string, any>;
	enabled: boolean;
	created_at: number;
}

export interface MCPConnectionStatus {
	status: 'success' | 'error';
	message: string;
	tools: any[];
}

/**
 * Get all MCP servers for the current user
 */
export const getMCPServers = async (token: string): Promise<MCPServer[]> => {
	let error = null;

	const res = await fetch(`${MCP_API_BASE_URL}/`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail || 'Failed to fetch MCP servers';
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

/**
 * Get a specific MCP server by ID
 */
export const getMCPServer = async (token: string, serverId: string): Promise<MCPServer> => {
	let error = null;

	const res = await fetch(`${MCP_API_BASE_URL}/${serverId}`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail || 'Failed to fetch MCP server';
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

/**
 * Create a new MCP server
 */
export const createMCPServer = async (token: string, server: MCPServerForm): Promise<MCPServer> => {
	let error = null;

	const res = await fetch(`${MCP_API_BASE_URL}/`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify(server)
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail || 'Failed to create MCP server';
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

/**
 * Update an existing MCP server
 */
export const updateMCPServer = async (
	token: string,
	serverId: string,
	server: MCPServerForm
): Promise<MCPServer> => {
	let error = null;

	const res = await fetch(`${MCP_API_BASE_URL}/${serverId}`, {
		method: 'PUT',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify(server)
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail || 'Failed to update MCP server';
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

/**
 * Delete an MCP server
 */
export const deleteMCPServer = async (token: string, serverId: string): Promise<void> => {
	let error = null;

	await fetch(`${MCP_API_BASE_URL}/${serverId}`, {
		method: 'DELETE',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail || 'Failed to delete MCP server';
			return null;
		});

	if (error) {
		throw error;
	}
};

/**
 * Toggle MCP server enabled state
 */
export const toggleMCPServer = async (
	token: string,
	serverId: string,
	enabled: boolean
): Promise<MCPServer> => {
	let error = null;

	const res = await fetch(`${MCP_API_BASE_URL}/${serverId}/toggle`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		},
		body: JSON.stringify({ enabled })
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail || 'Failed to toggle MCP server';
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

/**
 * Test connection to an MCP server
 */
export const testMCPConnection = async (
	token: string,
	serverId: string
): Promise<MCPConnectionStatus> => {
	let error = null;

	const res = await fetch(`${MCP_API_BASE_URL}/${serverId}/test`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail || 'Failed to test MCP connection';
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

/**
 * Get available tools from an MCP server
 */
export const getMCPTools = async (token: string, serverId: string): Promise<MCPTool[]> => {
	let error = null;

	const res = await fetch(`${MCP_API_BASE_URL}/${serverId}/tools`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail || 'Failed to fetch MCP tools';
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

/**
 * Sync tools from an MCP server to Open WebUI
 */
export const syncMCPTools = async (
	token: string,
	serverId: string
): Promise<{ detail: string; count: number }> => {
	let error = null;

	const res = await fetch(`${MCP_API_BASE_URL}/${serverId}/sync`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail || 'Failed to sync MCP tools';
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};
/**
 * Get list of MCP servers from marketplace
 * NOTE: Marketplace functionality removed - mcp_local module has been deleted
 */
export const getMCPServersList = async (
	token: string,
	params: {
		q?: string;
		page?: number;
		pageSize?: number;
	} = {}
): Promise<any> => {
	// Return empty marketplace data
	return {
		servers: [],
		pagination: {
			currentPage: 1,
			pageSize: params.pageSize || 50,
			totalPages: 0,
			totalCount: 0
		}
	};
};

/**
 * Get MCP server details from marketplace
 * NOTE: Marketplace functionality removed - mcp_local module has been deleted
 */
export const getMCPServerDetails = async (
	token: string,
	qualifiedName: string
): Promise<any> => {
	// Return null - no marketplace data available
	return null;
};
