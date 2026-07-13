import { useMemo } from "react";
import { Link, useNavigate, useParams } from "@tanstack/react-router";

import { useDogBreedsQuery, usePetsQuery, usePetPhotoQuery } from "@/entities/pet/model/pet.queries";
import { EditPetForm } from "@/features/edit-pet/ui/edit-pet-form";
import { appRoutes } from "@/shared/constants/routes";

import "./edit-pet-page.css";

export function EditPetPage() {
    const { petId } = useParams({ strict: false }) as { petId?: string };
    const navigate = useNavigate();
    const petsQuery = usePetsQuery();
    const breedsQuery = useDogBreedsQuery();

    const pet = useMemo(
        () => petsQuery.data?.find((item) => item.id === Number(petId)),
        [petsQuery.data, petId],
    );

    const photoQuery = usePetPhotoQuery(pet?.id ?? 0, pet?.pet_photo_object_key);
    const backParams = { petId: petId ?? "" };

    function goBack() {
        void navigate({
            to: appRoutes.petProfile,
            params: backParams,
        });
    }

    return (
        <main className="edit-pet-page">
            <header className="edit-pet-topbar">
                <Link className="edit-pet-back" to={appRoutes.petProfile} params={backParams} aria-label="Назад">
                    <svg width="29" height="29" viewBox="0 0 29 29" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                        <path d="M18.125 7.25L10.875 14.5L18.125 21.75" stroke="#9A9A9A" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                </Link>

            </header>

            {petsQuery.isLoading || breedsQuery.isLoading ? (
                <p className="edit-pet-state">Загружаем данные питомца...</p>
            ) : null}

            {!petsQuery.isLoading && !breedsQuery.isLoading && !pet ? (
                <p className="edit-pet-state">Питомец не найден</p>
            ) : null}

            {pet ? (
                <EditPetForm
                    pet={pet}
                    breeds={breedsQuery.data ?? []}
                    photoUrl={photoQuery.data ?? null}
                    onCancel={goBack}
                    onSaved={goBack}
                />
            ) : null}
        </main>
    );
}
