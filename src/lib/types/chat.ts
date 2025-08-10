export interface Chat {
	id: string;
	title: string;
	chat: any;
	updated_at: number;
	created_at: number;
	folder_id?: string | null;
	pinned?: boolean;
	meta?: any;
}

export interface ChatListResponse {
	chats: Chat[];
	total_pages: number;
	current_page: number;
}
