import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createChat, sendMessage, deleteChat } from "@/entities/chat/api/chat.api";
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

type DeleteChatVariables = {
    petId: number;
    chatId: number;
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

export function useDeleteChatMutation() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ petId, chatId }: DeleteChatVariables) => deleteChat(petId, chatId),
        onSuccess: (_data, variables) => {
            void queryClient.invalidateQueries({
                queryKey: chatQueryKeys.chats(variables.petId),
            });

            queryClient.removeQueries({
                queryKey: chatQueryKeys.messages(variables.petId, variables.chatId),
            });
        },
    });
}