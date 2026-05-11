import { useQuery } from "@tanstack/react-query";

import { getChatMessages, getPetChats } from "@/entities/chat/api/chat.api";

export const chatQueryKeys = {
    all: ["chat"] as const,
    chats: (petId: number) => [...chatQueryKeys.all, "chats", petId] as const,
    messages: (petId: number, chatId: number) =>
        [...chatQueryKeys.all, "messages", petId, chatId] as const,
};

export function usePetChatsQuery(petId: number, enabled: boolean = true) {
    return useQuery({
        queryKey: chatQueryKeys.chats(petId),
        queryFn: () => getPetChats(petId),
        enabled,
        staleTime: 60_000,
    });
}

export function useChatMessagesQuery(
    petId: number,
    chatId: number,
    enabled: boolean = true,
    refetchInterval: number | false = false,
) {
    return useQuery({
        queryKey: chatQueryKeys.messages(petId, chatId),
        queryFn: () => getChatMessages(petId, chatId),
        enabled,
        staleTime: 30_000,
        refetchInterval,
    });
}
