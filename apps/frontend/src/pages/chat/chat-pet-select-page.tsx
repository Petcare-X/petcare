import { useChatPetOptions } from "@/features/chat/model/chat-pet-options"
import { ChatPetOptionCard } from "@/features/chat/ui/chat-pet-option-card"

import "./chat-pet-selection-page.css"

export function ChatPetSelectPage() {
    const { pets, isLoading, isError } = useChatPetOptions();

    return (
        <div className="pet-selection-page">
            <h1>Консультация ИИ</h1>
            <p>Выберите питомца о котором хотите поговорить</p>

            <ul className="pet-options-list">
                {pets.map((pet) => (
                    <li key={pet.id}>
                        <ChatPetOptionCard pet={pet} />
                    </li>
                ))}
            </ul>
        </div>
    )
}