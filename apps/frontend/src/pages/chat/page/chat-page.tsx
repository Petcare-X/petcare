import { Link, useParams, useNavigate } from "@tanstack/react-router";
import { useEffect, useMemo, useRef, useState } from "react";

import { useSendMessageMutation, useDeleteChatMutation } from "@/entities/chat/model/chat.mutations";
import { useChatMessagesQuery } from "@/entities/chat/model/chat.queries";
import type { ChatMessage } from "@/entities/chat/model/chat.types";
import { appRoutes } from "@/shared/constants/routes";
import { usePetPhotoQuery, usePetsQuery } from "@/entities/pet/model/pet.queries";
import { MarkdownContent } from "@/shared/ui/markdown-content";
import { EmptyState } from "@/shared/ui/empty-state";

import "./chat-page.css"

export function ChatPage() {
    const { petId, chatId } = useParams({ strict: false }) as {
        petId?: string;
        chatId?: string;
    };

    const navigate = useNavigate();

    const petIdNumber = Number(petId);
    const chatIdNumber = Number(chatId);
    const hasValidParams = Number.isInteger(petIdNumber) && Number.isInteger(chatIdNumber);

    const [message, setMessage] = useState("");
    const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement | null>(null);
    const deleteConfirmRef = useRef<HTMLDivElement | null>(null);

    const messagesQuery = useChatMessagesQuery(petIdNumber, chatIdNumber, hasValidParams);
    const deleteChatMutation = useDeleteChatMutation();


    useEffect(() => {
        if (!hasValidParams) {
            return;
        }

        const hasGeneratingMessages = (messagesQuery.data ?? []).some(
            (item) =>
                item.role === "assistant" &&
                (item.status === "pending" || item.status === "in_progress"),
        );

        if (!hasGeneratingMessages) {
            return;
        }

        const intervalId = window.setInterval(() => {
            void messagesQuery.refetch();
        }, 1500);

        return () => {
            window.clearInterval(intervalId);
        };
    }, [hasValidParams, messagesQuery.data, messagesQuery.refetch]);

    
    const petsQuery = usePetsQuery();

    const pet = useMemo(
        () => (petsQuery.data ?? []).find((item) => String(item.id) === petId),
        [petsQuery.data, petId],
    );

    const photoQuery = usePetPhotoQuery(pet?.id ?? 0, Boolean(pet?.pet_photo_object_key));
    const sendMessageMutation = useSendMessageMutation();

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "end",
        });
    }, [messagesQuery.data?.length]);

    useEffect(() => {
        if (!isDeleteConfirmOpen) {
            return;
        }

        const handlePointerDown = (event: PointerEvent) => {
            if (!deleteConfirmRef.current?.contains(event.target as Node)) {
                setIsDeleteConfirmOpen(false);
            }
        };

        window.addEventListener("pointerdown", handlePointerDown);

        return () => {
            window.removeEventListener("pointerdown", handlePointerDown);
        };
    }, [isDeleteConfirmOpen]);


    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();

        const trimmedMessage = message.trim();

        if (!trimmedMessage || !hasValidParams) {
            return;
        }

        try {
            await sendMessageMutation.mutateAsync({
                petId: petIdNumber,
                chatId: chatIdNumber,
                payload: {
                    content: trimmedMessage,
                },
            });

            setMessage("");
        } catch (error) {
            console.error("failed to send message", error);
        }
    };

    async function handleDeleteChat(chatId: number) {
        if (!hasValidParams) return;

        try {
            await deleteChatMutation.mutateAsync({
                petId: petIdNumber,
                chatId,
            });

            await navigate({
                to: appRoutes.chatHistory,
                params: {
                    petId: String(petIdNumber),
                }
            });
        } catch (error) {
            console.error("failed to delete chat", error);
        }
    }

    return (
        <div className="chat-page">
            <header className="chat-header">
                <Link 
                    to={appRoutes.chatHistory} 
                    params={{petId: String(petIdNumber)}}
                    className="chat-back-button"
                >
                    <svg className="chat-back-icon" viewBox="0 0 25 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M5.90244 10.4498L14.1719 2.18024L11.9917 0L0.000324249 11.9914L11.9917 23.9827L14.1719 21.8024L5.90244 13.5331H24.667V10.4498H5.90244Z" fill="currentColor"/>
                    </svg>
                </Link>
                <div className="chat-pet-element">
                    {photoQuery.data ?
                    (<img
                        src={photoQuery.data}
                        alt={pet?.pet_name}
                        className="chat-pet-avatar"
                        />
                    ) : 
                        (<div className="chat-pet-avatar chat-image-placeholder">
                            {pet?.pet_name.slice(0, 2).toUpperCase()}
                        </div>)
                    }

                    <div className="chat-pet-info">
                        <h1 className="chat-pet-name">{pet?.pet_name}</h1>
                    </div>
                </div>
                <div ref={deleteConfirmRef} className="chat-delete-menu">
                    <button
                        type="button"
                        className="delete-chat"
                        aria-expanded={isDeleteConfirmOpen}
                        aria-haspopup="true"
                        onClick={() => setIsDeleteConfirmOpen((value) => !value)}
                    >
                        <svg className="delete-icon" viewBox="0 0 29 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M1 6.83333H3.91667M3.91667 6.83333H27.25M3.91667 6.83333L3.91667 27.25C3.91667 28.0235 4.22396 28.7654 4.77094 29.3124C5.31792 29.8594 6.05979 30.1667 6.83333 30.1667H21.4167C22.1902 30.1667 22.9321 29.8594 23.4791 29.3124C24.026 28.7654 24.3333 28.0235 24.3333 27.25V6.83333M8.29167 6.83333V3.91667C8.29167 3.14312 8.59896 2.40125 9.14594 1.85427C9.69292 1.30729 10.4348 1 11.2083 1H17.0417C17.8152 1 18.5571 1.30729 19.1041 1.85427C19.651 2.40125 19.9583 3.14312 19.9583 3.91667V6.83333M11.2083 14.125V22.875M17.0417 14.125V22.875" stroke="#A1A1A1" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                    </button>

                    {isDeleteConfirmOpen ? (
                        <button
                            type="button"
                            className="chat-delete-confirm-button"
                            disabled={deleteChatMutation.isPending}
                            onClick={() => void handleDeleteChat(chatIdNumber)}
                        >
                            {deleteChatMutation.isPending ? "Удаляем..." : "Удалить чат"}
                        </button>
                    ) : null}
                </div>
            </header>

                
            <section className="chat-messages">
                {!hasValidParams ? (
                    <EmptyState
                        title="Чат не найден"
                        description="Не удалось определить питомца или чат для этой страницы."
                    />
                ) : messagesQuery.isLoading ? (
                    <div className="chat-state-block">Загружаем сообщения...</div>
                ) : messagesQuery.isError ? (
                    <EmptyState
                        title="Не удалось загрузить чат"
                        description="Попробуйте открыть чат снова из списка питомцев."
                    />
                ) : messagesQuery.data?.length ? (
                    <div className="chat-messages-list">
                        {messagesQuery.data.map((item) => (
                            <div
                                key={item.id}
                                className={`chat-message-row ${getMessageRowClassName(item)}`}
                            >
                                <article className={`chat-message-bubble ${getBubbleClassName(item)}`}>
                                    <div className="chat-message-content">
                                        {item.role === "assistant" ? (
                                            <MarkdownContent content={item.content || getMessageFallback(item)} />
                                        ) : (
                                            item.content || getMessageFallback(item)
                                        )}
                                    </div>
                                    <div className="chat-message-meta">
                                        <span>{formatMessageTime(item.created_at)}</span>
                                        <span>{formatMessageStatus(item)}</span>
                                    </div>
                                </article>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                ) : (
                    <div className="chat-empty-state">
                        <div className="chat-empty-icon" aria-hidden="true">
                            <svg
                                className="chat-empty-icon-svg"
                                width="34"
                                height="33"
                                viewBox="0 0 34 33"
                                fill="none"
                                xmlns="http://www.w3.org/2000/svg"
                            >
                                <path d="M7.42425 26.6667L0 32.5V1.66667C0 0.7462 0.7462 0 1.66667 0H31.6667C32.5872 0 33.3333 0.7462 33.3333 1.66667V25C33.3333 25.9205 32.5872 26.6667 31.6667 26.6667H7.42425Z" fill="currentColor"/>
                            </svg>
                        </div>
                        <h2 className="chat-empty-title">Начните консультацию</h2>
                        <p className="chat-empty-description">
                            Спросите любой интересующий вас вопрос о вашем питомце
                        </p>
                    </div>
                )}
            </section>

            <form className="chat-composer" onSubmit={handleSubmit}>
                <input 
                    type="text" 
                    className="chat-input" 
                    value={message}
                    onChange={(event) => setMessage(event.target.value)}
                    placeholder={sendMessageMutation.isPending ? "Отправляем сообщение..." : "Задайте вопрос..."}
                    disabled={sendMessageMutation.isPending || !hasValidParams}
                />
                <button
                    type="submit"
                    className="chat-send-button"
                    disabled={
                        !message.trim() ||
                        !hasValidParams ||
                        sendMessageMutation.isPending
                    }
                >
                    <svg className="chat-send-icon" viewBox="0 0 25 23" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20.8121 0.00110239C21.4809 0.000708638 22.161 0.16956 22.7809 0.527344C24.6642 1.61466 25.3096 4.02298 24.2223 5.90626L15.7847 20.5203C14.6974 22.4035 12.289 23.049 10.4058 21.9617C9.46516 21.4185 8.83274 20.5431 8.57216 19.5722L6.88574 13.2781L16.7515 7.58168C17.2895 7.271 17.474 6.58267 17.1635 6.04469C16.8528 5.50693 16.1644 5.32233 15.6265 5.63271L5.76073 11.3302L1.15302 6.72145C-0.384542 5.18367 -0.384138 2.69104 1.15302 1.15356C1.8642 0.442339 2.85028 0.00023625 3.93698 0L20.8121 0.00110239Z" fill="currentColor"/>
                    </svg>
                </button>
            </form>
            {sendMessageMutation.isError ? (
                <p className="chat-composer-error">
                    Не удалось отправить сообщение. Попробуйте ещё раз.
                </p>
            ) : null}
        </div>
    );
}

function getBubbleClassName(message: ChatMessage) {
    if (message.role === "user") {
        return "is-user";
    }

    if (message.status === "failed") {
        return "is-error";
    }

    return "is-assistant";
}

function getMessageRowClassName(message: ChatMessage) {
    return message.role === "user" ? "is-user" : "is-assistant";
}

function getMessageFallback(message: ChatMessage) {
    if (message.status === "pending") {
        return "Готовим ответ...";
    }

    if (message.status === "in_progress") {
        return "ИИ печатает ответ...";
    }

    if (message.status === "failed") {
        return "Не удалось получить ответ.";
    }

    return "";
}

function formatMessageStatus(message: ChatMessage) {
    if (message.role === "user") {
        return "Вы";
    }

    if (message.status === "pending") {
        return "Ожидает";
    }

    if (message.status === "in_progress") {
        return "Пишет";
    }

    if (message.status === "failed") {
        return "Ошибка";
    }

    return "ИИ";
}

function formatMessageTime(value: string) {
    return new Intl.DateTimeFormat("ru-RU", {
        hour: "2-digit",
        minute: "2-digit",
    }).format(new Date(value));
}

function formatChatDate(value: string) {
    return new Intl.DateTimeFormat("ru-RU", {
        day: "2-digit",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
    }).format(new Date(value));
}
