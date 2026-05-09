import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createChat, sendMessage } from "@/entities/chat/api/chat.api";
import { chatQueryKeys } from "@/entities/chat/model/chat.queries";
import type {
    CreateChatPayload,
    SendMessagePayload,
} from "@/entities/chat/model/chat.types";

type CreateChatVariables = {
    petId: number;
    payload: CreateChatPayload;
};

type SendMessageVariables = {
    petId: number;
    chatId: number;
    payload: SendMessagePayload;
};

export function useCreateChatMutation() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ petId, payload }: CreateChatVariables) => createChat(petId, payload),
        onSuccess: (_chat, variables) => {
            void queryClient.invalidateQueries({
                queryKey: chatQueryKeys.chats(variables.petId),
            });
        },
    });
}

export function useSendMessageMutation() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ petId, chatId, payload }: SendMessageVariables) =>
            sendMessage(petId, chatId, payload),
        onSuccess: (_response, variables) => {
            void queryClient.invalidateQueries({
                queryKey: chatQueryKeys.messages(variables.petId, variables.chatId),
            });
        },
    });
}
