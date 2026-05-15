import { usePetPhotoQuery, usePetsQuery } from "@/entities/pet/model/pet.queries"
import { useMemo } from "react";
import { Link, useNavigate } from "@tanstack/react-router";
import { useParams } from "@tanstack/react-router";
import { appRoutes } from "@/shared/constants/routes";
import { usePetChatsQuery } from "@/entities/chat/model/chat.queries";

import "./chat-history-page.css"
import { useCreateChatMutation } from "@/entities/chat/model/chat.mutations";

export function ChatHistoryPage() {
    const navigate = useNavigate();
    const { petId } = useParams({ strict: false }) as { petId?: string };

    const petIdNumber = Number(petId);
    const hasValidPetId = Number.isInteger(petIdNumber) && petIdNumber > 0;

    const petQuery = usePetsQuery();
    
    const pet = useMemo(
        () => (petQuery.data ?? []).find((pet) => String(pet.id) === petId),
        [petQuery.data, petId],
    )

    const photoQuery = usePetPhotoQuery(pet?.id ?? 0,  Boolean(pet?.pet_photo_object_key));

    const chatsQuery = usePetChatsQuery(petIdNumber, hasValidPetId)
    
    const createChatMutation = useCreateChatMutation();

    async function handleNewChatCreation() {
        if (!hasValidPetId) {
            return
        }

        try {
            const chat = await createChatMutation.mutateAsync({
                petId: petIdNumber,
                payload: {
                    chat_title: `Чат о ${pet?.pet_name}`
                },
            });

            await navigate({
                to: appRoutes.chat,
                params: {
                    petId: String(petIdNumber),
                    chatId: String(chat.id),
                },
            });
        } catch (error) {
            console.error("failed to create chat", error);
        }
    }

    return (
        <>
            <header className="chats-history-header">
                <Link
                    to={appRoutes.chatSelectPet}
                    className="chat-history-back-button"
                >
                    <svg className="chat-history-back-icon" viewBox="0 0 25 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M5.90244 10.4498L14.1719 2.18024L11.9917 0L0.000324249 11.9914L11.9917 23.9827L14.1719 21.8024L5.90244 13.5331H24.667V10.4498H5.90244Z" fill="currentColor"/>
                    </svg>
                </Link>
            </header>

            <div className="chat-history-pet-conteiner">
                {photoQuery.data ?
                    (<img
                        src={photoQuery.data}
                        alt={pet?.pet_name}
                        className="chat-pet-option-image"
                    />
                ) : 
                    (<div className="chat-pet-option-image image-placeholder">
                        {pet?.pet_name.slice(0, 2).toUpperCase()}
                    </div>)
                }

                <div className="chat-history-pet-text">
                    <h1 className="chat-history-pet-name">{pet?.pet_name}</h1>
                    <p className="chat-history-pet-subtitle">История чатов</p>
                </div>
            </div>

            <section className="chat-history-content">
                <button
                    type="button"
                    className="new-chat-button"
                    onClick={handleNewChatCreation}
                >
                    + новый чат
                </button>

                {chatsQuery.data?.length ? (
                    <ul className="chat-history-list">
                        {chatsQuery.data.map((chat) => (
                            <li key={chat.id} className="chat-history-item">
                                <Link
                                    to={appRoutes.chat}
                                    params={{
                                        petId: String(chat.pet_id),
                                        chatId: String(chat.id),
                                    }}
                                    className="previous-chat-option"
                                >
                                    <p className="previous-chat-title">{chat.chat_title}</p>
                                    <p className="previous-chat-date">{formatChatDate(chat.created_at)}</p>
                                </Link>
                            </li>
                        ))
                        }
                    </ul>
                ) : null}
            </section>
        </>
    )
}

function formatChatDate(value: string) {
    return new Intl.DateTimeFormat("ru-RU", {
        day: "numeric",
        month: "long",
        year: "numeric",
    }).format(new Date(value));
}
