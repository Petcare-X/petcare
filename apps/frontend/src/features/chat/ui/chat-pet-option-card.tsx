import { Link } from "@tanstack/react-router";

import { usePetPhotoQuery } from "@/entities/pet/model/pet.queries";
import type { ChatPetOption } from "@/features/chat/model/chat-pet-options";
import { appRoutes } from "@/shared/constants/routes";

import "./chat-pet-option.css";

type ChatPetOptionCardProps = {
    pet: ChatPetOption;
}

export function ChatPetOptionCard({ pet }: ChatPetOptionCardProps) {
    const photoQuery = usePetPhotoQuery(pet.id, Boolean(pet.photoObjectKey));

    return (
        <Link
            className="chat-pet-option-card"
            to={appRoutes.chat}
            params={{ petId: String(pet.id) }}
        >
            <div className="chat-pet-option-card-main">
                <img
                    src={photoQuery.data}
                    alt={pet.name}
                    className="chat-pet-option-image"
                />

                <div>
                    <p className="chat-pet-option-name">{pet.name}</p>
                    <p className="chat-pet-option-breed">{pet.breed}</p>
                </div>
            </div>

            <svg className="chat-icon" viewBox="0 0 30 29" xmlns="http://www.w3.org/2000/svg">
                <path d="M6.49622 23.3333L0 28.4375V1.45833C0 0.652925 0.652925 0 1.45833 0H27.7083C28.5138 0 29.1667 0.652925 29.1667 1.45833V21.875C29.1667 22.6804 28.5138 23.3333 27.7083 23.3333H6.49622Z" fill="currentColor"/>
            </svg>
        </Link>
    )
}