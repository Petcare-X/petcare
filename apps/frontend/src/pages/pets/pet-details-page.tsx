import { useMemo } from "react";
import { Link, useParams } from "@tanstack/react-router";
import { appRoutes } from "@/shared/constants/routes";

import { mapPetToCardView } from "@/widgets/pet-card/model/pet-info-formating";

import {
    useDogBreedsQuery,
    usePetsQuery,
    usePetPhotoQuery
} from "@/entities/pet/model/pet.queries";

import './pet-details-page.css';

export function PetDetailsPage() {
    const { petId } = useParams({ strict: false }) as { petId?: string };

    const petsQuery = usePetsQuery();
    const breedsQuery = useDogBreedsQuery();


    const pet = useMemo(() => {
        const foundPet = petsQuery.data?.find((item) => item.id === Number(petId));

        if (!foundPet) {
            return undefined;
        }

        return mapPetToCardView(foundPet, breedsQuery.data ?? []);
    }, [breedsQuery.data, petsQuery.data, petId]);

    const photoQuery = usePetPhotoQuery(pet?.id ?? 0, Boolean(pet?.photoObjectKey));

    const isLoading = petsQuery.isLoading || breedsQuery.isLoading;
    const petInitial = pet?.name?.slice(0, 1).toUpperCase() ?? "?";

    return (
        <main className="pet-details-page">
            {photoQuery.data ? (
                <img className="pet-profile-bg" src={photoQuery.data} alt="" />
            ) : (
                <div className="pet-profile-bg pet-profile-bg--empty" />
            )}
            
            <section className="pet-profile-header">
                <Link className="back-home" to={appRoutes.home}>
                    <svg width="11" height="18" viewBox="0 0 11 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M8.91892 18L0 9L8.91892 0L11 2.1L4.16216 9L11 15.9L8.91892 18Z" fill="#FAFAFA"/>
                    </svg>
                </Link>

                <Link className="change-info" to={appRoutes.home}>
                    Изменить
                </Link>
            </section>
            
            {petsQuery.isLoading || breedsQuery.isLoading ? (
                <p>Загружаем питомца...</p>
            ) : (
                <section className="pet-base-info">
                    <p className="pet-profile-name">{pet?.name ?? "Питомец не найден"}</p>
                    <p className="pet-profile-breed">{pet?.breed ?? "Порода не указана"}</p>
                </section>
            )}
            
            <section className="for-share">
                <Link className="shared-quantity" to={appRoutes.home}>
                    <svg width="20" height="27" viewBox="0 0 20 27" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M0 26.25C0 20.7271 4.47715 16.25 10 16.25C15.5229 16.25 20 20.7271 20 26.25H0ZM10 15C5.85625 15 2.5 11.6438 2.5 7.5C2.5 3.35625 5.85625 0 10 0C14.1437 0 17.5 3.35625 17.5 7.5C17.5 11.6438 14.1437 15 10 15Z" fill="white"/>
                    </svg>
                    <span className="shared-quantity-value">2</span>
                </Link> 

                <Link className="share-pet" to={appRoutes.home}>
                    <svg width="23" height="24" viewBox="0 0 23 24" fill="none" xmlns="http://www.w3.org/2000/svg"> 
                        <path d="M11.25 0L19.0089 7.75887L17.2411 9.5266L12.5 4.78552V16.7677H10V4.78552L5.25889 9.5266L3.49111 7.75887L11.25 0ZM0 19.2677V14.2677H2.5V19.2677C2.5 19.9581 3.05965 20.5177 3.75 20.5177H18.75C19.4404 20.5177 20 19.9581 20 19.2677V14.2677H22.5V19.2677C22.5 21.3389 20.8211 23.0177 18.75 23.0177H3.75C1.67894 23.0177 0 21.3389 0 19.2677Z" fill="#FAFAFA"/> 
                    </svg>
                </Link>
            </section>
            
            <section className="pet-detailed-info">
                
                <div className="pet-params-avatar">
                        {/* сюда аватар питомца */}
                </div>
                
                <p className="pet-detailed-title">Параметры {pet?.name}</p>

                <button type="button" className="pet-details-toggle">
                    <svg className="arrow-up" width="15" height="9" viewBox="0 0 15 9" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M7.50005 3.27269L1.66667 9L0 7.36363L7.50005 0L15 7.36363L13.3333 9L7.50005 3.27269Z" fill="#FAFAFA"/>
                    </svg>

                    <svg className="arrow-down" width="15" height="9" viewBox="0 0 15 9" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M7.49995 5.72731L13.3333 0L15 1.63637L7.49995 9L0 1.63637L1.66666 0L7.49995 5.72731Z" fill="#FAFAFA"/>
                    </svg>
                </button>
            </section>

            <section className="pet-documents">
                <div className="pet-documents-header">
                    <p className="pet-documents-title">Документы</p>

                    <Link className="pet-documents-add" to={appRoutes.home}>
                        + Добавить
                    </Link>
                </div>

                <div className="pet-documents-body">
                    {/* сюда доки документы */}
                </div>
            </section>
        </main>
    );
}
