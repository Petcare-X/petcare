export type Chat = {
    id: number;
    pet_id: number;
    chat_title: string;
    created_at: string;
};

export type CreateChatPayload = {
    chat_title?: string;
    chat_custom_instructions?: string | null;
};

export type MessageRole = "user" | "assistant" | "system";

export type MessageStatus = "pending" | "in_progress" | "completed" | "failed";

export type ChatMessage = {
    id: number;
    chat_id: number;
    user_id: number;
    role: MessageRole;
    content: string;
    parent_message_id: number | null;
    status: MessageStatus;
    error_message: string | null;
    created_at: string;
};

export type SendMessagePayload = {
    chat_id?: number | null;
    content: string;
};

export type SendMessageResponse = {
    user_message: ChatMessage | null;
    assistant_message: ChatMessage | null;
};
