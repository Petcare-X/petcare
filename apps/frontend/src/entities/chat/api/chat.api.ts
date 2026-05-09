import axios from "axios";

import { apiClient } from "@/shared/api/client";

import type {
    Chat,
    ChatMessage,
    CreateChatPayload,
    SendMessagePayload,
    SendMessageResponse,
} from "@/entities/chat/model/chat.types";

export async function getPetChats(petId: number): Promise<Chat[]> {
    try {
        const response = await apiClient.get<Chat[]>(`/llm-chat/chats/${petId}`);

        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error) && error.response?.status === 404) {
            return [];
        }

        throw error;
    }
}

export async function createChat(petId: number, payload: CreateChatPayload): Promise<Chat> {
    const response = await apiClient.post<Chat>(`/llm-chat/${petId}/create-chat`, payload);

    return response.data;
}

export async function getChatMessages(petId: number, chatId: number): Promise<ChatMessage[]> {
    const response = await apiClient.get<ChatMessage[]>(`/llm-chat/${petId}/${chatId}/messages`);

    return response.data;
}

export async function deleteChat(petId: number, chatId: number): Promise<void> {
    await apiClient.delete(`/llm-chat/${petId}/${chatId}`);
}


export async function sendMessage(
    petId: number,
    chatId: number,
    payload: SendMessagePayload,
): Promise<SendMessageResponse> {
    const response = await apiClient.post<SendMessageResponse>(
        `/llm-chat/${petId}/${chatId}/send-message`,
        payload,
    );

    return response.data;
}