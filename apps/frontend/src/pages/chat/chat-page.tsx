import { Link, useParams, useSearch } from "@tanstack/react-router"
import { useMemo, useState, useEffect } from "react";

import { appRoutes } from "@/shared/constants/routes";
import { usePetPhotoQuery, usePetsQuery } from "@/entities/pet/model/pet.queries";

import "./chat-page.css"

export function ChatPage() {
    const { petId, chatId } = useParams({ strict: false }) as {
        petId?: string;
        chatId?: string;
    };

    const [isOnline, setIsOnline] = useState(navigator.onLine);
    const [message, setMessage] = useState("");
    const [isHistoryOpen, setIsHistoryOpen] = useState(false);

    useEffect(() => {
        const handleOnline = () => setIsOnline(true);
        const handleOffline = () => setIsOnline(false);

        window.addEventListener("online", handleOnline);
        window.addEventListener("offline", handleOffline);

        return () => {
            window.removeEventListener("online", handleOnline),
            window.removeEventListener("offline", handleOffline)
        };
    },[]);
    
    const petsQuery = usePetsQuery();

    const pet = useMemo(
        () => (petsQuery.data ?? []).find((item) => String(item.id) === petId),
        [petsQuery.data, petId],
    );

    const photoQuery = usePetPhotoQuery(pet?.id ?? 0, Boolean(pet?.pet_photo_object_key));

    const handleSubmit = (event: React.FormEvent) => {
        event.preventDefault();
        if (!message.trim()) return;

        setMessage("");
    };

    return (
        <div className="chat-page">
            <header className="chat-header">
                <Link to={appRoutes.chatSelectPet} className="chat-back-button">
                    <svg className="chat-back-icon" viewBox="0 0 25 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M5.90244 10.4498L14.1719 2.18024L11.9917 0L0.000324249 11.9914L11.9917 23.9827L14.1719 21.8024L5.90244 13.5331H24.667V10.4498H5.90244Z" fill="currentColor"/>
                    </svg>
                </Link>
                <div className="chat-pet-element">
                    <img 
                        src={photoQuery.data}
                        alt={pet?.pet_name}
                        className="chat-pet-avatar"
                    />
                    <div className="chat-pet-info">
                        <h1 className="chat-pet-name">{pet?.pet_name}</h1>
                        <p className={isOnline ? "chat-status online" : "chat-status offline"}>
                            {isOnline ? "в сети" : "не в сети"}
                        </p>
                    </div>
                </div>

                
                <button
                    type="button"
                    className="chat-history-button"
                    onClick={() => setIsHistoryOpen(true)}
                >
                    чаты
                </button>
            </header>

            <section className="chat-messages">
                <div>

                </div>
            </section>

            <form className="chat-composer" onSubmit={handleSubmit}>
                <input 
                    type="text" 
                    className="chat-input" 
                    value={message}
                    onChange={(event) => setMessage(event.target.value)}
                    placeholder="Ваш вопрос..."
                />
                <button
                    type="submit"
                    className="chat-send-button"
                >
                    <svg className="chat-send-icon" viewBox="0 0 25 23" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20.8121 0.00110239C21.4809 0.000708638 22.161 0.16956 22.7809 0.527344C24.6642 1.61466 25.3096 4.02298 24.2223 5.90626L15.7847 20.5203C14.6974 22.4035 12.289 23.049 10.4058 21.9617C9.46516 21.4185 8.83274 20.5431 8.57216 19.5722L6.88574 13.2781L16.7515 7.58168C17.2895 7.271 17.474 6.58267 17.1635 6.04469C16.8528 5.50693 16.1644 5.32233 15.6265 5.63271L5.76073 11.3302L1.15302 6.72145C-0.384542 5.18367 -0.384138 2.69104 1.15302 1.15356C1.8642 0.442339 2.85028 0.00023625 3.93698 0L20.8121 0.00110239Z" fill="currentColor"/>
                    </svg>
                </button>
            </form>

            <button
                type="button"
                className={`chat-history-overlay ${isHistoryOpen? "is-open" : ""}`}
                aria-label="Закрыть историю чатов"
                onClick={() => setIsHistoryOpen(false)}
            />

            <aside className={`chats-history-sheet ${isHistoryOpen ? "is-open" : ""}`}>
                <div className="chats-history-top-panel">
                    <h2>Чаты о питомце</h2>
                    <button 
                        type="button"
                        className="history-close-button"
                        onClick={() => setIsHistoryOpen(false)}>
                        скрыть
                    </button>
                </div>

                <ul className="chats-history-list">
                    <li>Чат 1</li>
                    <li>Чат 2</li>
                    <li>Чат 3</li>
                </ul>
            </aside>
        </div>
    );
}