import { useMemo, useState } from "react";
import { createPortal } from "react-dom";
import { Link } from "@tanstack/react-router";

import { useDogBreedsQuery, usePetsQuery } from "@/entities/pet/model/pet.queries";

import { CreatePetForm } from "@/features/add-pet/ui/create-pet-form";
import { AcceptInviteForm } from "@/features/add-pet/ui/accept-pet-invite-form";
import { PetCard } from "@/widgets/pet-card/pet-card";
import { mapPetToCardView } from "@/widgets/pet-card/model/pet-info-formating";

import { appRoutes } from '@/shared/constants/routes';
import { EmptyState } from "@/shared/ui/empty-state";


import './home-page.css';

export function HomePage() {
    const [addPetMode, setAddPetMode] = useState<"menu" | "create" | "invite" | null>(null);
    const petsQuery = usePetsQuery();
    const breedsQuery = useDogBreedsQuery();

    const pets = useMemo(
        () => (petsQuery.data ?? []).map((pet) => mapPetToCardView(pet, breedsQuery.data ?? [])),
        [breedsQuery.data, petsQuery.data],
    );
    const firstPetName = pets[0]?.name ?? "питомец";

    return (
        <>
            <section className="pets-section">
                <div className="section-row">
                    <h2 className="section-title">Мои питомцы</h2>
                    {pets.length > 0 ? (
                        <button
                            type="button"
                            className="add-pet-button"
                            onClick={() => setAddPetMode("menu")}
                        >
                            + Добавить
                        </button>
                    ) : null}
                </div>

                {addPetMode ? createPortal(
                    <div className="create-pet-overlay">
                        <div className="create-pet-modal">
                            {addPetMode === "menu" ? (
                                <div className="add-pet-menu">
                                    <div className="add-pet-menu-heading">
                                        <p className="add-pet-menu-title">Добавить питомца</p>
                                        <p className="add-pet-menu-subtitle">
                                            Выберите, хотите ли вы создать новый профиль питомца
                                            или добавить его по коду доступа.
                                        </p>
                                    </div>

                                    <div className="add-pet-menu-options">
                                        <button
                                            type="button"
                                            className="add-pet-menu-option add-pet-menu-option-primary"
                                            onClick={() => setAddPetMode("create")}
                                        >
                                            <span className="add-pet-menu-option-title">
                                                Создать нового питомца
                                            </span>
                                            <span className="add-pet-menu-option-text">
                                                Заполните имя, породу, возраст, вес и добавьте фото.
                                            </span>
                                        </button>

                                        <button
                                            type="button"
                                            className="add-pet-menu-option"
                                            onClick={() => setAddPetMode("invite")}
                                        >
                                            <span className="add-pet-menu-option-title">
                                                Добавить по коду
                                            </span>
                                            <span className="add-pet-menu-option-text">
                                                Введите код шеринга, чтобы получить доступ к питомцу.
                                            </span>
                                        </button>
                                    </div>

                                    <div className="create-pet-actions">
                                        <button type="button" onClick={() => setAddPetMode(null)}>
                                            Отмена
                                        </button>
                                    </div>
                                </div>
                            ) : null}

                            {addPetMode === "create" ? (
                                <CreatePetForm onCreated={() => setAddPetMode(null)} />
                            ) : null}

                            {addPetMode === "invite" ? (
                                <AcceptInviteForm
                                    onAccepted={() => setAddPetMode(null)}
                                    onCancel={() => setAddPetMode(null)}
                                />
                            ) : null}
                        </div>
                    </div>,
                    document.body,
                ) : null}


                {petsQuery.isLoading || breedsQuery.isLoading ? (
                    <div className="pets-loading">Загружаем питомцев...</div>
                ) : null}

                {petsQuery.isError ? (
                    <div className="pets-error">Не удалось загрузить питомцев</div>
                ) : null}

                {!petsQuery.isLoading && !petsQuery.isError && pets.length === 0 ? (
                    <EmptyState
                        title="Давайте знакомиться!"
                        description="Добавьте своего питомца, и мы создадим его профиль."
                        actionText="+ добавить"
                        onAction={() => setAddPetMode("menu")}
                    />
                ) : null}

                {pets.length > 0 ? (
                    <ul className="pets-list">
                        {pets.map((pet) => (
                            <li key={pet.id}>
                                <PetCard pet={pet} />
                            </li>
                        ))}
                    </ul>
                ) : null}
            </section>

            <section className="services-section">
                <h2 className="section-title">Сервисы</h2>
                
                <div className="service-list">
                    <Link className="service-card" to={appRoutes.map}>
                        <svg className="service-icon" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <rect width="42" height="42" rx="9" fill="#49AA35"/>
                            <path d="M21.0002 21C21.596 21 22.1061 20.7879 22.5304 20.3636C22.9547 19.9393 23.1668 19.4292 23.1668 18.8334C23.1668 18.2375 22.9547 17.7275 22.5304 17.3031C22.1061 16.8788 21.596 16.6667 21.0002 16.6667C20.4043 16.6667 19.8943 16.8788 19.47 17.3031C19.0456 17.7275 18.8335 18.2375 18.8335 18.8334C18.8335 19.4292 19.0456 19.9393 19.47 20.3636C19.8943 20.7879 20.4043 21 21.0002 21ZM21.0002 28.9625C23.2029 26.9403 24.837 25.1031 25.9022 23.4511C26.9675 21.799 27.5002 20.332 27.5002 19.05C27.5002 17.082 26.8727 15.4705 25.6179 14.2156C24.363 12.9608 22.8238 12.3334 21.0002 12.3334C19.1766 12.3334 17.6373 12.9608 16.3825 14.2156C15.1276 15.4705 14.5002 17.082 14.5002 19.05C14.5002 20.332 15.0328 21.799 16.0981 23.4511C17.1634 25.1031 18.7974 26.9403 21.0002 28.9625ZM21.0002 31.8334C18.0932 29.3597 15.922 27.0622 14.4866 24.9406C13.0512 22.8191 12.3335 20.8556 12.3335 19.05C12.3335 16.3417 13.2047 14.184 14.947 12.5771C16.6894 10.9702 18.7071 10.1667 21.0002 10.1667C23.2932 10.1667 25.3109 10.9702 27.0533 12.5771C28.7957 14.184 29.6668 16.3417 29.6668 19.05C29.6668 20.8556 28.9491 22.8191 27.5137 24.9406C26.0783 27.0622 23.9071 29.3597 21.0002 31.8334Z" fill="#FAFAFA"/>
                        </svg>
                        <div className="service-text">
                            <p className="service-title">Места</p>
                            <p className="service-description">Где погулять</p>
                        </div>
                    </Link>
                    <Link className="service-card" to={appRoutes.map}>
                        <svg className="service-icon" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <rect width="42" height="42" rx="9" fill="#C2410C"/>
                            <path d="M16.667 11.25H17.4795C17.4795 10.9504 17.3146 10.675 17.0504 10.5336C16.7862 10.3923 16.4656 10.4077 16.2163 10.574L16.667 11.25ZM23.167 11.25L23.6177 10.574C23.3684 10.4077 23.0478 10.3923 22.7836 10.5336C22.5194 10.675 22.3545 10.9504 22.3545 11.25H23.167ZM15.8545 12.875C15.8545 13.3237 16.2183 13.6875 16.667 13.6875C17.1157 13.6875 17.4795 13.3237 17.4795 12.875H15.8545ZM22.3545 12.875C22.3545 13.3237 22.7183 13.6875 23.167 13.6875C23.6157 13.6875 23.9795 13.3237 23.9795 12.875H22.3545ZM25.6045 15.156V18.8333H27.2295V15.156H25.6045ZM22.0837 22.3542H17.7503V23.9792H22.0837V22.3542ZM14.2295 18.8333V15.156H12.6045V18.8333H14.2295ZM15.3149 13.1279L17.1177 11.926L16.2163 10.574L14.4135 11.7758L15.3149 13.1279ZM25.4204 11.7758L23.6177 10.574L22.7163 11.926L24.5191 13.1279L25.4204 11.7758ZM15.8545 11.25V12.875H17.4795V11.25H15.8545ZM22.3545 11.25V12.875H23.9795V11.25H22.3545ZM17.7503 22.3542C15.8058 22.3542 14.2295 20.7778 14.2295 18.8333H12.6045C12.6045 21.6754 14.9084 23.9792 17.7503 23.9792V22.3542ZM25.6045 18.8333C25.6045 20.7778 24.0281 22.3542 22.0837 22.3542V23.9792C24.9257 23.9792 27.2295 21.6754 27.2295 18.8333H25.6045ZM27.2295 15.156C27.2295 13.7977 26.5507 12.5293 25.4204 11.7758L24.5191 13.1279C25.1972 13.58 25.6045 14.341 25.6045 15.156H27.2295ZM14.2295 15.156C14.2295 14.341 14.6368 13.58 15.3149 13.1279L14.4135 11.7758C13.2833 12.5293 12.6045 13.7977 12.6045 15.156H14.2295ZM19.1045 23.1667V29.6667H20.7295V23.1667H19.1045ZM21.0003 31.5625H23.167V29.9375H21.0003V31.5625ZM25.0628 29.6667V27.8939H23.4378V29.6667H25.0628ZM25.3337 27.6231H26.417V25.9981H25.3337V27.6231ZM25.0628 27.8939C25.0628 27.7444 25.1841 27.6231 25.3337 27.6231V25.9981C24.2866 25.9981 23.4378 26.8469 23.4378 27.8939H25.0628ZM23.167 31.5625C24.214 31.5625 25.0628 30.7137 25.0628 29.6667H23.4378C23.4378 29.8163 23.3166 29.9375 23.167 29.9375V31.5625ZM19.1045 29.6667C19.1045 30.7137 19.9533 31.5625 21.0003 31.5625V29.9375C20.8507 29.9375 20.7295 29.8163 20.7295 29.6667H19.1045ZM28.8545 26.8101C28.8545 27.2589 28.4907 27.6226 28.042 27.6226V29.2476C29.3881 29.2476 30.4795 28.1563 30.4795 26.8101H28.8545ZM28.042 27.6226C27.593 27.6226 27.2295 27.2591 27.2295 26.8106H25.6045C25.6045 28.1572 26.6962 29.2476 28.042 29.2476V27.6226ZM27.2295 26.8106C27.2295 26.3615 27.5936 25.9976 28.042 25.9976V24.3726C26.6955 24.3726 25.6045 25.4647 25.6045 26.8106H27.2295ZM28.042 25.9976C28.4907 25.9976 28.8545 26.3614 28.8545 26.8101H30.4795C30.4795 25.4639 29.3881 24.3726 28.042 24.3726V25.9976Z" fill="#FAFAFA"/>
                        </svg>
                        <div className="service-text">
                            <p className="service-title">Клиники</p>
                            <p className="service-description">Подходящие врачи</p>
                        </div>
                    </Link>
                    <Link className="service-card" to={appRoutes.map}>
                        <svg className="service-icon" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <rect width="42" height="42" rx="9" fill="#818CF8"/>
                            <path d="M17.4462 16.0287L20 18.5825L26.7279 11.8546C27.509 11.0735 28.7753 11.0735 29.5563 11.8546L17.4462 23.9647C17.7981 24.5603 18 25.2549 18 25.9967C18 28.2058 16.2091 29.9967 14 29.9967C11.7909 29.9967 10 28.2058 10 25.9967C10 23.7876 11.7909 21.9967 14 21.9967C14.7418 21.9967 15.4365 22.1986 16.032 22.5505L18.5858 19.9967L16.032 17.4429C15.4365 17.7948 14.7418 17.9967 14 17.9967C11.7909 17.9967 10 16.2058 10 13.9967C10 11.7876 11.7909 9.9967 14 9.9967C16.2091 9.9967 18 11.7876 18 13.9967C18 14.7385 17.7981 15.4332 17.4462 16.0287ZM22.8255 21.408L29.5563 28.1388C28.7753 28.9199 27.509 28.9199 26.7279 28.1388L21.4113 22.8222L22.8255 21.408ZM15.4142 24.5825C15.0523 24.2206 14.5523 23.9967 14 23.9967C12.8954 23.9967 12 24.8921 12 25.9967C12 27.1013 12.8954 27.9967 14 27.9967C15.1046 27.9967 16 27.1013 16 25.9967C16 25.4444 15.7761 24.9444 15.4142 24.5825ZM15.4142 15.4109C15.7761 15.049 16 14.549 16 13.9967C16 12.8921 15.1046 11.9967 14 11.9967C12.8954 11.9967 12 12.8921 12 13.9967C12 15.1013 12.8954 15.9967 14 15.9967C14.5523 15.9967 15.0523 15.7729 15.4142 15.4109Z" fill="white"/>
                        </svg>
                        <div className="service-text">
                            <p className="service-title">Салоны</p>
                            <p className="service-description">Уход и забота</p>
                        </div>
                    </Link>
                    <Link className="service-card" to={appRoutes.documents}>
                        <svg className="service-icon" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <rect width="42" height="42" rx="9" fill="#F9B116"/>
                        <path d="M23.1668 10.1667H14.5002C13.9255 10.1667 13.3744 10.395 12.9681 10.8013C12.5618 11.2076 12.3335 11.7587 12.3335 12.3334V29.6667C12.3335 30.2413 12.5618 30.7924 12.9681 31.1988C13.3744 31.6051 13.9255 31.8334 14.5002 31.8334H27.5002C28.0748 31.8334 28.6259 31.6051 29.0322 31.1988C29.4386 30.7924 29.6668 30.2413 29.6668 29.6667V16.6667M23.1668 10.1667L29.6668 16.6667M23.1668 10.1667L23.1668 16.6667H29.6668M25.3335 22.0834H16.6668M25.3335 26.4167H16.6668M18.8335 17.75H16.6668" stroke="#FAFAFA" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                        <div className="service-text">
                            <p className="service-title">Документы</p>
                            <p className="service-description">Паспорта и справки</p>
                        </div>
                    </Link>
                </div>
            </section>
        </>
    );
};
