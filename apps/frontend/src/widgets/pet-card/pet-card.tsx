import { Link } from "@tanstack/react-router";

import { usePetPhotoQuery } from "@/entities/pet/model/pet.queries";
import type { PetCardView } from "@/entities/pet/model/pet.types";
import { appRoutes } from "@/shared/constants/routes";

import arrowIcon from "@/pages/home/assets/arrowIcon.svg";
import calendarPet from "@/pages/home/assets/calendarPet.svg";
import weightPet from "@/pages/home/assets/weightPet.svg";

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
                            <img src={calendarPet} alt="" className="pet-meta-icon" />
                            {pet.age}
                        </span>

                        <span className="pet-meta-item">
                            <img src={weightPet} alt="" className="pet-meta-icon" />
                            {pet.weight}
                        </span>
                    </div>
                </div>
            </div>

            <img src={arrowIcon} alt="" className="arrow-icon" />
        </Link>
    );
}
