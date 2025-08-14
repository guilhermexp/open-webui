// Basic tools API for Open WebUI
export interface Tool {
	id: string;
	name: string;
	description: string;
}

export const getTools = async (): Promise<Tool[]> => {
	// Return empty array for now - tools functionality can be implemented later
	return [];
};

export const getTool = async (id: string): Promise<Tool | null> => {
	// Return null for now - tools functionality can be implemented later
	return null;
};