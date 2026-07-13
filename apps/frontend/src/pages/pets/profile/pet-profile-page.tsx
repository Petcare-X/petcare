import { useEffect, useMemo, useRef, useState } from "react";
import type { PointerEvent as ReactPointerEvent } from "react";
import { Link, useParams } from "@tanstack/react-router";
import { appRoutes } from "@/shared/constants/routes";

import { DocumentsList } from "@/widgets/document-list/documents-list";
import { mapPetToCardView } from "@/widgets/pet-card/model/pet-info-formating";
import { useCreateInvite } from "@/features/manage-share/model/use-create-invite";
import { useSharedUsersQuery } from "@/entities/invite/model/shared-users.queries";
import {
    useDogBreedsQuery,
    usePetsQuery,
    usePetPhotoQuery
} from "@/entities/pet/model/pet.queries";

import './pet-profile-page.css';
import { usePetDocumentsQuery } from "@/entities/document/model/document.queries";
import { UploadDocumentForm } from "@/features/upload-document/ui/upload-document-form";
import { createPortal } from "react-dom";
import { useDeleteDocument } from "@/features/delete-document/model/use-delete-document";

type SheetMode = "collapsed" | "mid" | "expanded";

function shouldIgnoreSheetDrag(target: EventTarget | null) {
    if (!(target instanceof Element)) {
        return false;
    }

    return Boolean(
        target.closest(
            "button, a, input, textarea, select, label, [role='button'], [data-sheet-no-drag]",
        ),
    );
}

export function PetProfilePage() {
    const { petId } = useParams({ strict: false }) as { petId?: string };
    const petIdNumber = Number(petId);

    const petsQuery = usePetsQuery();
    const breedsQuery = useDogBreedsQuery();
    const documentsQuery = usePetDocumentsQuery(petIdNumber, Number.isFinite(petIdNumber) && petIdNumber > 0);

    const createInvite = useCreateInvite();
    const [inviteCode, setInviteCode] = useState<string | null>(null);

    const [sharingIsOpen, setSharingIsOpen] = useState(false);
    const [isParamsOpen, setIsParamsOpen] = useState(false);
    const [uploadIsOpen, setUploadIsOpen] = useState(false);
    const [viewportHeight, setViewportHeight] = useState(() => window.innerHeight);
    const [sheetMode, setSheetMode] = useState<SheetMode>("collapsed");
    const [sheetOffset, setSheetOffset] = useState(0);
    const [isDraggingSheet, setIsDraggingSheet] = useState(false);

    const sharedUsersQuery = useSharedUsersQuery(
        petIdNumber, 
        Number.isFinite(petIdNumber) && petIdNumber > 0
    );

    const sharedUsersCount = sharedUsersQuery.data?.length ?? 0;

    const contentRef = useRef<HTMLDivElement | null>(null);
    const dragStateRef = useRef<{
        pointerId: number | null;
        startY: number;
        startOffset: number;
    }>({
        pointerId: null,
        startY: 0,
        startOffset: 0,
    });


    const pet = useMemo(() => {
        const foundPet = petsQuery.data?.find((item) => item.id === Number(petId));

        if (!foundPet) {
            return undefined;
        }

        return mapPetToCardView(foundPet, breedsQuery.data ?? []);
    }, [breedsQuery.data, petsQuery.data, petId]);

    const photoQuery = usePetPhotoQuery(pet?.id ?? 0, pet?.photoObjectKey);

    const sheetMetrics = useMemo(() => {
        const topInset = 96;
        const maxHeight = Math.max(viewportHeight - topInset, 320);
        const collapsedPeek = 220;
        const midPeek = Math.min(460, Math.round(maxHeight * 0.66));
        const expanded = 0;
        const mid = Math.max(0, maxHeight - midPeek);
        const collapsed = Math.max(0, maxHeight - collapsedPeek);

        return {
            topInset,
            maxHeight,
            offsets: {
                expanded,
                mid,
                collapsed,
            },
        };
    }, [viewportHeight]);

    useEffect(() => {
        setInviteCode(null);
    }, [petIdNumber]);

    useEffect(() => {
        const handleResize = () => {
            setViewportHeight(window.innerHeight);
        };

        window.addEventListener("resize", handleResize, { passive: true });

        return () => {
            window.removeEventListener("resize", handleResize);
        };
    }, []);

    useEffect(() => {
        setSheetOffset(sheetMetrics.offsets[sheetMode]);
    }, [sheetMetrics, sheetMode]);

    useEffect(() => {
        if (!sharingIsOpen || !petIdNumber || inviteCode || createInvite.isPending) {
            return;
        }

        createInvite.mutate(
            {
                pet_id: petIdNumber,
                max_uses: 1,
                expires_at: null,
            },
            {
                onSuccess: (invite) => {
                    setInviteCode(invite.invite_code);
                },
            },
        );
    }, [sharingIsOpen, petIdNumber, inviteCode, createInvite]);

    useEffect(() => {
        if (sheetMode !== "expanded" && contentRef.current) {
            contentRef.current.scrollTop = 0;
        }
    }, [sheetMode]);

    const petParams = pet
        ? [
            { label: "Имя", value: pet.name },
            { label: "Порода", value: pet.breed },
            { label: "Возраст", value: pet.age },
            { label: "Вес", value: pet.weight },
        ]
        : [];

    const setNearestSheetMode = (offset: number) => {
        const nextMode = (Object.entries(sheetMetrics.offsets) as Array<[SheetMode, number]>)
            .reduce(
                (closest, entry) =>
                    Math.abs(entry[1] - offset) < Math.abs(closest[1] - offset) ? entry : closest,
                ["collapsed", sheetMetrics.offsets.collapsed] as [SheetMode, number],
            )[0];

        setSheetMode(nextMode);
    };

    const handleSheetPointerDown = (event: ReactPointerEvent<HTMLElement>) => {
        if (shouldIgnoreSheetDrag(event.target)) {
            return;
        }

        dragStateRef.current = {
            pointerId: event.pointerId,
            startY: event.clientY,
            startOffset: sheetOffset,
        };

        setIsDraggingSheet(true);
        event.currentTarget.setPointerCapture(event.pointerId);
    };

    const handleSheetPointerMove = (event: ReactPointerEvent<HTMLElement>) => {
        if (!isDraggingSheet || dragStateRef.current.pointerId !== event.pointerId) {
            return;
        }

        const deltaY = event.clientY - dragStateRef.current.startY;
        const nextOffset = Math.min(
            sheetMetrics.offsets.collapsed,
            Math.max(sheetMetrics.offsets.expanded, dragStateRef.current.startOffset + deltaY),
        );

        setSheetOffset(nextOffset);
    };

    const finishSheetDrag = (pointerId: number) => {
        if (dragStateRef.current.pointerId !== pointerId) {
            return;
        }

        setIsDraggingSheet(false);
        dragStateRef.current.pointerId = null;
        setNearestSheetMode(sheetOffset);
    };

    const handleSheetPointerUp = (event: ReactPointerEvent<HTMLElement>) => {
        finishSheetDrag(event.pointerId);
    };

    const handleSheetPointerCancel = (event: ReactPointerEvent<HTMLElement>) => {
        finishSheetDrag(event.pointerId);
    };


    const deleteDocumentMutation = useDeleteDocument();

    const [documentToDeleteId, setDocumentToDeleteId] = useState<number | null>(null);

    const handleRequestDeleteDocument = (documentId: number) => {
        setDocumentToDeleteId(documentId);
    }

    const handleConfirmDocumentDelete = () => {
        if (!petIdNumber || documentToDeleteId === null) {
            return;
        }

        deleteDocumentMutation.mutate(
            {
                petId: petIdNumber,
                documentId: documentToDeleteId,
            },
            {
                onSuccess: () => {
                    setDocumentToDeleteId(null);
                },
            },
        );
    }

    const handleCancelDocumentDelete = () => {
        setDocumentToDeleteId(null);
    }

    return (
        <main
            className="pet-details-page"
            style={{
                backgroundImage: `url(${photoQuery.data})`,
                backgroundPosition: "center",
                backgroundSize: "cover",
                backgroundRepeat: "no-repeat",
                ["--pet-sheet-offset" as string]: `${sheetOffset}px`,
                ["--pet-sheet-max-height" as string]: `${sheetMetrics.maxHeight}px`,
                ["--pet-sheet-top-inset" as string]: `${sheetMetrics.topInset}px`,
            }}
        >
            { photoQuery.data ?
                null :
                (<div className="pet-details-backdrop" />)
            }

            <section className="pet-profile-header">
                <Link className="back-home" to={appRoutes.home}>
                    <svg className="back-home-icon" viewBox="0 0 11 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M8.91892 18L0 9L8.91892 0L11 2.1L4.16216 9L11 15.9L8.91892 18Z" fill="currentColor"/>
                    </svg>
                </Link>

                <Link
                    className="change-info"
                    to={appRoutes.editPetProfile}
                    params={{ petId: String(pet?.id ?? petId ?? "") }}
                >
                    Изменить
                </Link>
            </section>

            <section
                className={`pet-profile-info pet-profile-info--${sheetMode} ${isDraggingSheet ? "pet-profile-info--dragging" : ""}`}
                onPointerDown={handleSheetPointerDown}
                onPointerMove={handleSheetPointerMove}
                onPointerUp={handleSheetPointerUp}
                onPointerCancel={handleSheetPointerCancel}
            >
                <div className="pet-sheet-drag-zone" aria-hidden="true">
                    <span className="pet-sheet-handle" />
                </div>

                <div className="pet-profile-info-top">
                    {petsQuery.isLoading || breedsQuery.isLoading ? (
                        <p>Загружаем питомца...</p>
                    ) : (
                        <section className="pet-base-info">
                            <p className="pet-profile-name">{pet?.name ?? "Питомец не найден"}</p>
                            <p className="pet-profile-breed">{pet?.breed ?? "Порода не указана"}</p>
                        </section>
                    )}

                    <section className="for-share">
                        <div className="shared-quantity">
                            <svg width="20" height="27" viewBox="0 0 20 27" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M0 26.25C0 20.7271 4.47715 16.25 10 16.25C15.5229 16.25 20 20.7271 20 26.25H0ZM10 15C5.85625 15 2.5 11.6438 2.5 7.5C2.5 3.35625 5.85625 0 10 0C14.1437 0 17.5 3.35625 17.5 7.5C17.5 11.6438 14.1437 15 10 15Z" fill="white"/>
                            </svg>
                            <span className="shared-quantity-value">{sharedUsersCount}</span>
                        </div>

                        <button type="button" className="share-pet-button" onClick={() => setSharingIsOpen(true)}>
                            <svg width="23" height="24" viewBox="0 0 23 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M11.25 0L19.0089 7.75887L17.2411 9.5266L12.5 4.78552V16.7677H10V4.78552L5.25889 9.5266L3.49111 7.75887L11.25 0ZM0 19.2677V14.2677H2.5V19.2677C2.5 19.9581 3.05965 20.5177 3.75 20.5177H18.75C19.4404 20.5177 20 19.9581 20 19.2677V14.2677H22.5V19.2677C22.5 21.3389 20.8211 23.0177 18.75 23.0177H3.75C1.67894 23.0177 0 21.3389 0 19.2677Z" fill="#FAFAFA"/>
                            </svg>
                        </button>
                    </section>
                </div>

                <div ref={contentRef} className="pet-profile-info-scroll" data-sheet-no-drag>
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
                                ) : (null)}
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

                            <button
                                type="button"
                                className="pet-documents-add"
                                onClick={() => setUploadIsOpen(true)}
                            >
                                + Добавить
                            </button>

                            {uploadIsOpen ? createPortal(
                                <div
                                    className="pet-add-documents-overlay"
                                    onClick={() => setUploadIsOpen(false)}
                                >
                                    <div
                                        className="pet-add-documents-modal"
                                        onClick={(event) => event.stopPropagation()}
                                    >
                                        <UploadDocumentForm
                                            petId={petIdNumber}
                                            onUploaded={() => setUploadIsOpen(false)}
                                            onCancel={() => setUploadIsOpen(false)}
                                        />
                                    </div>
                                </div>,
                                document.body,
                            ) : null}
                        </div>

                        <div className="pet-documents-body">
                            {documentsQuery.isLoading ? (
                                <p>Загружаем документы...</p>
                            ) : documentsQuery.isError ? (
                                <p>ОШИБКА</p>
                            ) : (
                                <DocumentsList
                                    petId={petIdNumber}
                                    documents={documentsQuery.data ?? []}
                                    onRequestDelete={handleRequestDeleteDocument}
                                />
                            )}
                        </div>

                        {documentToDeleteId !== null ? createPortal(
                            <div
                                className="pet-delete-document-overlay"
                                onClick={handleCancelDocumentDelete}
                            >
                                <div
                                    className="pet-delete-document-modal"
                                    onClick={(event) => event.stopPropagation()}
                                >
                                    <p className="pet-delete-document-title">
                                        Удалить документ?
                                    </p>
                                    <p className="pet-delete-document-text">
                                        Документ будет удален из профиля питомца и из хранилища.
                                    </p>

                                    <div className="pet-delete-document-actions">
                                        <button
                                            type="button"
                                            className="pet-delete-document-button pet-delete-document-button-secondary"
                                            onClick={handleCancelDocumentDelete}
                                            disabled={deleteDocumentMutation.isPending}
                                        >
                                            Отмена
                                        </button>
                                        <button
                                            type="button"
                                            className="pet-delete-document-button pet-delete-document-button-danger"
                                            onClick={handleConfirmDocumentDelete}
                                            disabled={deleteDocumentMutation.isPending}
                                        >
                                            {deleteDocumentMutation.isPending ? "Удаляем..." : "Удалить"}
                                        </button>
                                    </div>
                                </div>
                            </div>,
                            document.body,
                        ) : null}
                    </section>
                </div>
            </section>

            <button
                className={`pet-sharing-overlay ${sharingIsOpen ? "is-open" : ""}`}
                onClick={() => setSharingIsOpen(false)}
            />

            <aside className={`sharing-element ${sharingIsOpen ? "is-open" : ""}`}>
                <img className="pet-sharing-image" src={photoQuery.data}/>
                <div className="sharing-pet-info-conteiner">
                    <div className="sharing-pet-info">
                        <p className="sharing-pet-name">{pet?.name}</p>
                        <p className="sharing-pet-code">
                            {createInvite.isPending
                                ? "Генерируем код..."
                                : inviteCode ?? "Код пока недоступен"}
                        </p>
                    </div>

                    <button
                        type="button"
                        className="pet-sharing-copy-button"
                        onClick={async () => {
                            if (!inviteCode) {
                                return;
                            }
                        
                            await navigator.clipboard.writeText(inviteCode);
                        }}
                        disabled={!inviteCode}
                    >
                        Копировать код
                    </button>
                </div>
            </aside>
        </main>
    );
}
