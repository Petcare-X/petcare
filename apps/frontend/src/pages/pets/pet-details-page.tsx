import { useMemo, useState } from "react";
import { Link, useParams } from "@tanstack/react-router";
import { appRoutes } from "@/shared/constants/routes";

import { mapPetToCardView } from "@/widgets/pet-card/model/pet-info-formating";

import { getPetDocumentDownloadUrl } from "@/entities/document/api/document.api";
import { useDocumentQueries } from "@/entities/document/model/document.queries";
import type { Document } from "@/entities/document/model/document.types";
import {
    useDogBreedsQuery,
    usePetsQuery,
    usePetPhotoQuery
} from "@/entities/pet/model/pet.queries";

import './pet-details-page.css';

export function PetDetailsPage() {
    const { petId } = useParams({ strict: false }) as { petId?: string };
    const [isParamsOpen, setIsParamsOpen] = useState(false);

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
    const documentsQuery = useDocumentQueries(pet?.id);

    const isLoading = petsQuery.isLoading || breedsQuery.isLoading;
    const petInitial = pet?.name?.slice(0, 1).toUpperCase() ?? "?";
    const petParams = pet
        ? [
            { label: "Имя", value: pet.name },
            { label: "Порода", value: pet.breed },
            { label: "Возраст", value: pet.age },
            { label: "Вес", value: pet.weight },
        ]
        : [];
    const documents = documentsQuery.data ?? [];
    const documentCards = documents.length > 0
        ? documents.map((document) => ({
            id: String(document.id),
            name: getDocumentName(document),
            meta: `${getDocumentFileType(document)} • ${formatDocumentDate(document.uploaded_at)}`,
            documentId: document.id,
        }))
        : [
            {
                id: "vet-passport-placeholder",
                name: "Вет-паспорт",
                meta: "PDF • 05.12.2025",
                documentId: null,
            },
            {
                id: "xray-placeholder",
                name: "Рентген",
                meta: "PDF • 22.09.2023",
                documentId: null,
            },
        ];

    async function handleDownloadDocument(documentId: number) {
        if (!pet) {
            return;
        }

        const documentDownload = await getPetDocumentDownloadUrl(pet.id, documentId);
        window.open(documentDownload.download_url, "_blank", "noopener,noreferrer");
    }

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
            
            <section className={`pet-detailed-info ${isParamsOpen ? "pet-detailed-info--open" : ""}`}>
                <button
                    type="button"
                    className="pet-detailed-summary"
                    aria-expanded={isParamsOpen}
                    aria-label={isParamsOpen ? "Скрыть параметры питомца" : "Показать параметры питомца"}
                    disabled={!pet}
                    onClick={() => setIsParamsOpen((value) => !value)}
                >
                    <span className="pet-params-avatar">
                        {photoQuery.data ? (
                            <img className="pet-params-avatar-image" src={photoQuery.data} alt={pet?.name ?? ""} />
                        ) : (
                            <span className="pet-params-avatar-initial">{petInitial}</span>
                        )}
                    </span>
                    
                    <span className="pet-detailed-title">Параметры {pet?.name ?? "питомца"}</span>

                    <span className="pet-details-toggle" aria-hidden="true">
                        <svg className="arrow-up" width="15" height="9" viewBox="0 0 15 9" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M7.50005 3.27269L1.66667 9L0 7.36363L7.50005 0L15 7.36363L13.3333 9L7.50005 3.27269Z" fill="#FAFAFA"/>
                        </svg>

                        <svg className="arrow-down" width="15" height="9" viewBox="0 0 15 9" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M7.49995 5.72731L13.3333 0L15 1.63637L7.49995 9L0 1.63637L1.66666 0L7.49995 5.72731Z" fill="#FAFAFA"/>
                        </svg>
                    </span>
                </button>

                {isParamsOpen && (
                    <div className="pet-params-list">
                        {petParams.map((param) => (
                            <div className="pet-param-row" key={param.label}>
                                <span className="pet-param-label">{param.label}</span>
                                <span className="pet-param-value">{param.value}</span>
                            </div>
                        ))}
                    </div>
                )}
            </section>

            <section className="pet-documents">
                <div className="pet-documents-header">
                    <p className="pet-documents-title">Документы</p>

                    <Link className="pet-documents-add" to={appRoutes.home}>
                        + Добавить
                    </Link>
                </div>

                <div className="pet-documents-body">
                    {documentsQuery.isLoading ? (
                        <p className="pet-documents-state">Загружаем документы...</p>
                    ) : null}

                    {documentsQuery.isError ? (
                        <p className="pet-documents-state">Не удалось загрузить документы</p>
                    ) : null}

                    {!documentsQuery.isLoading && !documentsQuery.isError ? documentCards.map((document) => (
                        <article className="pet-document-card" key={document.id}>
                            <div className="pet-document-icon" aria-hidden="true">
                                <svg width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <rect width="42" height="42" rx="9" fill="#A1A1A1"/>
                                    <path d="M29.6668 16.6667L23.1668 10.1667H14.5002C13.9255 10.1667 13.3744 10.395 12.9681 10.8013C12.5618 11.2077 12.3335 11.7588 12.3335 12.3334V29.6667C12.3335 30.2414 12.5618 30.7925 12.9681 31.1988C13.3744 31.6051 13.9255 31.8334 14.5002 31.8334H27.5002C28.0748 31.8334 28.6259 31.6051 29.0322 31.1988C29.4386 30.7925 29.6668 30.2414 29.6668 29.6667V16.6667ZM23.1668 10.1667L23.1668 16.6667H29.6668M25.3335 22.0834H16.6668M25.3335 26.4167H16.6668M18.8335 17.7501H16.6668" stroke="#FAFAFA" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
                                </svg>
                            </div>

                            <div className="pet-document-info">
                                <p className="pet-document-name">{document.name}</p>
                                <p className="pet-document-meta">{document.meta}</p>
                            </div>

                            <button
                                type="button"
                                className="pet-document-download"
                                aria-label={`Скачать документ ${document.name}`}
                                disabled={document.documentId === null}
                                onClick={() => {
                                    if (document.documentId !== null) {
                                        void handleDownloadDocument(document.documentId);
                                    }
                                }}
                            >
                                <svg width="21" height="22" viewBox="0 0 21 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M10.5 2V14M10.5 14L5.5 9M10.5 14L15.5 9" stroke="#FAFAFA" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                    <path d="M3 19H18" stroke="#FAFAFA" strokeWidth="2" strokeLinecap="round"/>
                                </svg>
                            </button>
                        </article>
                    )) : null}
                </div>
            </section>
        </main>
    );
}

function getDocumentName(document: Document): string {
    return document.custom_name || document.document_type_name || "Документ";
}

function getDocumentFileType(document: Document): string {
    if (document.content_type?.includes("pdf")) {
        return "PDF";
    }

    const extension = document.object_key.split(".").pop()?.trim();

    if (extension) {
        return extension.toUpperCase();
    }

    return "Файл";
}

function formatDocumentDate(value: string | null): string {
    if (!value) {
        return "без даты";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "без даты";
    }

    return new Intl.DateTimeFormat("ru-RU", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
    }).format(date);
}
