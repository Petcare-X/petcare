import { Link } from "@tanstack/react-router";

import { usePetPhotoQuery } from "@/entities/pet/model/pet.queries";
import type { PetCardView } from "@/entities/pet/model/pet.types";
import { appRoutes } from "@/shared/constants/routes";

import "./pet-card.css"

type PetCardProps = {
    pet: PetCardView;
};

export function PetCard({ pet }: PetCardProps) {
    const photoQuery = usePetPhotoQuery(pet.id, Boolean(pet.photoObjectKey));

    return (
        <Link
            className="pet-card"
            to={appRoutes.petProfile}
            params={{ petId: String(pet.id) }}
        >
            <div className="pet-main">
                {photoQuery.data ? (
                    <img src={photoQuery.data} alt={pet.name} className="pet-image" />
                ) : (
                    <div className="pet-image pet-image-placeholder">
                        {pet.name.slice(0, 1).toUpperCase()}
                    </div>
                )}

                <div className="pet-info">
                    <p className="pet-name">{pet.name}</p>
                    <p className="pet-breed">{pet.breed}</p>

                    <div className="pet-meta">
                        <span className="pet-meta-item">
                            <svg className="pet-meta-icon" width="13" height="15" viewBox="0 0 13 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M8.9248 0.799988V3.29999M3.9248 0.799988V3.29999M0.799805 5.79999H12.0498M2.0498 2.04999H10.7998C11.4902 2.04999 12.0498 2.60963 12.0498 3.29999V12.05C12.0498 12.7403 11.4902 13.3 10.7998 13.3H2.0498C1.35945 13.3 0.799805 12.7403 0.799805 12.05V3.29999C0.799805 2.60963 1.35945 2.04999 2.0498 2.04999Z" stroke="#F97316" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                            {pet.age}
                        </span>

                        <span className="pet-meta-item">
                            <svg className="pet-meta-icon" width="12" height="15" viewBox="0 0 12 15" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M1.5 0C1.5 0.38463 1.8675 0.75 2.25 0.75H9.74996C10.1346 0.75 10.5 0.3825 10.5 0H12C12 1.24264 10.9926 2.25 9.74996 2.25H6.74996L6.75071 3.79651C9.71014 4.1659 12 6.69052 12 9.75V14.25C12 14.6642 11.6642 15 11.25 15H0.75C0.335783 15 0 14.6642 0 14.25V9.75C0 6.6903 2.29028 4.16547 5.25004 3.79642L5.24996 2.25H2.25C1.005 2.25 0 1.245 0 0H1.5ZM5.99996 5.25C3.5712 5.25 1.5 7.32 1.5 9.75V13.5H10.5V9.75C10.5 7.3212 8.42876 5.25 5.99996 5.25ZM5.99996 6.75C6.55639 6.75 7.07734 6.90142 7.52396 7.16535L5.46964 9.21967C5.17676 9.51255 5.17676 9.98745 5.46964 10.2803C5.74001 10.5507 6.16549 10.5715 6.45964 10.3427L6.53036 10.2803L8.58461 8.226C8.84854 8.67262 8.99996 9.19365 8.99996 9.75C8.99996 11.4068 7.65686 12.75 5.99996 12.75C4.34315 12.75 3 11.4068 3 9.75C3 8.09317 4.34315 6.75 5.99996 6.75Z" fill="#F97316"/>
                            </svg>
                            {pet.weight}
                        </span>
                    </div>
                </div>
            </div>

            <svg className="arrow-icon" viewBox="0 0 15 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M9.0746 11.6673L0 2.59272L2.59274 0L14.26 11.6673L2.59274 23.3344L0 20.7417L9.0746 11.6673Z" fill="currentColor"/>
            </svg>
        </Link>
    );
}
