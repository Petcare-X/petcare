import { useMemo, useRef, useState } from "react";
import type { CSSProperties, PointerEvent } from "react";
import { useNavigate } from "@tanstack/react-router";

import { YMap, YMapDefaultFeaturesLayer, YMapDefaultSchemeLayer, YMapMarker } from "@/shared/lib/ymaps";

import "./map-page.css";
import { appRoutes } from "@/shared/constants/routes";
import { useClinicsQuery, useFriendlyQuery, useGroomingsQuery } from "@/entities/map-point/model/map.queries";
import { mapClinicToPlace, mapDogPlaceToPlace, mapGroomingToPlace, type MapPlace } from "@/entities/map-point/model/map.types";

type PlaceType = "clinic" | "place" | "salon";

type PlaceFilter = {
    id: PlaceType;
    title: string;
    color: string;
};

type FilterStyle = CSSProperties & {
    "--filter-color": string;
};

type SheetDragState = {
    startY: number;
    startHeight: number;
    currentHeight: number;
    isDragging: boolean;
};

type FilterDragState = {
    startX: number;
    startY: number;
    startScrollLeft: number;
    isDragging: boolean;
    didDrag: boolean;
    suppressNextClick: boolean;
    pressedFilterId: PlaceType | null;
};

const SHEET_COLLAPSED = 164;
const SHEET_HALF = 430;
const SHEET_EXPANDED = 660;
const SHEET_TOP_OFFSET = 72;
const FILTER_DRAG_THRESHOLD = 8;

const filters: PlaceFilter[] = [
    { id: "clinic", title: "Клиники", color: "#d34b1c" },
    { id: "place", title: "Места", color: "#49aa35" },
    { id: "salon", title: "Салоны", color: "#7c83ff" },
];

const initialSheetDrag: SheetDragState = {
    startY: 0,
    startHeight: SHEET_HALF,
    currentHeight: SHEET_HALF,
    isDragging: false,
};

const initialFilterDrag: FilterDragState = {
    startX: 0,
    startY: 0,
    startScrollLeft: 0,
    isDragging: false,
    didDrag: false,
    suppressNextClick: false,
    pressedFilterId: null,
};

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

function clamp(value: number, min: number, max: number) {
    return Math.min(Math.max(value, min), max);
}

function getMaxSheetHeight() {
    return Math.min(SHEET_EXPANDED, window.innerHeight - SHEET_TOP_OFFSET);
}

function getClosestSheetHeight(height: number) {
    return [SHEET_COLLAPSED, SHEET_HALF, getMaxSheetHeight()].reduce((closest, point) => {
        return Math.abs(point - height) < Math.abs(closest - height) ? point : closest;
    }, SHEET_COLLAPSED);
}

function getFilterIdFromTarget(target: EventTarget) {
    const button = (target as HTMLElement).closest<HTMLButtonElement>("[data-filter-id]");

    return (button?.dataset.filterId as PlaceType | undefined) ?? null;
}

function releasePointerCapture(element: Element, pointerId: number) {
    if (element.hasPointerCapture(pointerId)) {
        element.releasePointerCapture(pointerId);
    }
}

function GlobeIcon() {
    return (
        <svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <rect x="1" y="1" width="28" height="28" rx="5" fill="#FFEDD5" />
            <rect x="1" y="1" width="28" height="28" rx="5" stroke="#FFEDD5" strokeWidth="2" strokeLinecap="round" />
            <path d="M15.0003 25.8334C9.01724 25.8334 4.16699 20.9831 4.16699 15C4.16699 9.01693 9.01724 4.16669 15.0003 4.16669C20.9834 4.16669 25.8337 9.01693 25.8337 15C25.8337 20.9831 20.9834 25.8334 15.0003 25.8334ZM12.5195 23.3064C11.4767 21.0947 10.8374 18.6554 10.6966 16.0834H6.40071C6.82983 19.5246 9.27641 22.3393 12.5195 23.3064ZM12.8669 16.0834C13.0299 18.7254 13.7846 21.2072 15.0003 23.398C16.216 21.2072 16.9708 18.7254 17.1337 16.0834H12.8669ZM23.5999 16.0834H19.3041C19.1632 18.6554 18.524 21.0947 17.4812 23.3064C20.7242 22.3393 23.1708 19.5246 23.5999 16.0834ZM6.40071 13.9167H10.6966C10.8374 11.3446 11.4767 8.90526 12.5195 6.69363C9.27641 7.66079 6.82983 10.4755 6.40071 13.9167ZM12.8669 13.9167H17.1337C16.9708 11.2747 16.216 8.79279 15.0003 6.60201C13.7846 8.79279 13.0299 11.2747 12.8669 13.9167ZM17.4812 6.69363C18.524 8.90526 19.1632 11.3446 19.3041 13.9167H23.5999C23.1708 10.4755 20.7242 7.66079 17.4812 6.69363Z" fill="#EA580C" />
        </svg>
    );
}

function PhoneIcon() {
    return (
        <svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <rect x="1" y="1" width="28" height="28" rx="5" fill="#FFEDD5" />
            <rect x="1" y="1" width="28" height="28" rx="5" stroke="#FFEDD5" strokeWidth="2" strokeLinecap="round" />
            <path d="M24.75 19.7883V23.6191C24.75 24.1879 24.3103 24.6598 23.743 24.6998C23.2692 24.7333 22.8827 24.75 22.5833 24.75C13.0103 24.75 5.25 16.9897 5.25 7.41667C5.25 7.11735 5.26674 6.73078 5.30021 6.25696C5.34032 5.6897 5.81218 5.25 6.38085 5.25H10.2118C10.4898 5.25 10.7227 5.46062 10.7507 5.73728C10.7757 5.98566 10.799 6.18507 10.8206 6.33552C11.0397 7.86595 11.4873 9.32264 12.1278 10.6699C12.2306 10.8862 12.1635 11.1451 11.9687 11.2842L9.63051 12.9545C11.054 16.2795 13.7205 18.946 17.0456 20.3695L18.7127 18.0354C18.8536 17.8382 19.1156 17.7704 19.3344 17.8743C20.6817 18.5142 22.1382 18.9613 23.6684 19.1799C23.8179 19.2014 24.016 19.2245 24.2627 19.2494C24.5394 19.2773 24.75 19.5102 24.75 19.7883Z" fill="#EA580C" />
        </svg>
    );
}

function PawIcon() {
    return (
        <svg width="23" height="23" viewBox="0 0 23 23" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M4.50925 13.701C3.2156 13.851 2.01805 12.6897 1.83476 11.1073C1.59657 9.05308 2.42622 7.04265 3.72006 6.89287C5.01371 6.74282 6.29868 8.65955 6.51955 10.5644C6.70287 12.1467 5.80316 13.551 4.50925 13.701Z" fill="#FAFAFA" />
            <path d="M14.6413 20.4688C12.7996 20.4172 12.1025 19.5916 10.9214 19.5583C9.74007 19.5252 8.99807 20.3104 7.15638 20.2586C4.7454 20.1907 3.04046 17.1476 5.28234 15.2301C8.06841 12.8476 8.92842 9.77651 11.1942 9.84028C13.4603 9.9041 14.1465 13.0184 16.7945 15.5538C18.9252 17.594 17.0521 20.5367 14.6413 20.4688Z" fill="#FAFAFA" />
            <path d="M11.8992 5.84789C12.1164 3.94282 13.3979 2.02369 14.6917 2.17105C15.9859 2.31872 16.8193 4.3275 16.585 6.38206C16.4046 7.96487 15.2094 9.12839 13.9155 8.98074C12.6215 8.83336 11.7188 7.43069 11.8992 5.84789Z" fill="#FAFAFA" />
            <path d="M6.00668 6.08483C5.88829 4.02042 6.83315 2.06146 8.13344 1.98707C9.43355 1.9124 10.6053 3.90047 10.7151 5.81473C10.8065 7.40514 9.82652 8.75477 8.52641 8.82944C7.22607 8.90408 6.09808 7.67526 6.00668 6.08483Z" fill="#FAFAFA" />
            <path d="M17.6534 14.0706C16.37 13.8483 15.5504 12.3955 15.8222 10.8259C16.1496 8.93673 17.5404 7.09516 18.8235 7.3177C20.1068 7.54004 20.8224 9.59374 20.4693 11.6312C20.1973 13.2007 18.9365 14.2929 17.6534 14.0706Z" fill="#FAFAFA" />
        </svg>
    );
}

type MapCanvasProps = {
    places: MapPlace[];
};

function MapCanvas({ places }: MapCanvasProps) {
    const location = {
        center: [37.623082, 55.75254], // starting position [lng, lat]
        zoom: 9 // starting zoom
    } as const;

    return (
        <YMap location={location}>
            <YMapDefaultSchemeLayer />
            <YMapDefaultFeaturesLayer />

            {places.map((place) => (
                <YMapMarker
                    key={`${place.type}-${place.id}`}
                    coordinates={place.coordinates}
                >
                    <button type="button" className={`custom-marker custom-marker-${place.type}`}>
                        {place.title}
                    </button>
                </YMapMarker>
            ))}
        </YMap>
    );
}

type PlaceFiltersProps = {
    activeFilter: PlaceType | "";
    onChange: (filter: PlaceType) => void;
};

function PlaceFilters({ activeFilter, onChange }: PlaceFiltersProps) {
    const listRef = useRef<HTMLDivElement>(null);
    const dragRef = useRef<FilterDragState>(initialFilterDrag);

    const handlePointerDown = (event: PointerEvent<HTMLDivElement>) => {
        const list = listRef.current;

        if (!list) {
            return;
        }

        dragRef.current = {
            ...initialFilterDrag,
            startX: event.clientX,
            startY: event.clientY,
            startScrollLeft: list.scrollLeft,
            isDragging: true,
            pressedFilterId: getFilterIdFromTarget(event.target),
        };
        event.currentTarget.setPointerCapture(event.pointerId);
    };

    const handlePointerMove = (event: PointerEvent<HTMLDivElement>) => {
        const list = listRef.current;
        const drag = dragRef.current;

        if (!list || !drag.isDragging) {
            return;
        }

        const offsetX = event.clientX - drag.startX;
        const offsetY = event.clientY - drag.startY;
        const isHorizontalDrag = Math.abs(offsetX) > FILTER_DRAG_THRESHOLD && Math.abs(offsetX) > Math.abs(offsetY);

        if (isHorizontalDrag) {
            drag.didDrag = true;
        }

        if (drag.didDrag) {
            list.scrollLeft = drag.startScrollLeft - offsetX;
        }
    };

    const handlePointerEnd = (event: PointerEvent<HTMLDivElement>) => {
        const drag = dragRef.current;

        if (!drag.isDragging) {
            return;
        }

        if (drag.didDrag) {
            drag.suppressNextClick = true;
        } else if (drag.pressedFilterId) {
            onChange(drag.pressedFilterId);
            drag.suppressNextClick = true;
        }

        drag.isDragging = false;
        drag.pressedFilterId = null;
        releasePointerCapture(event.currentTarget, event.pointerId);
    };

    const handleClick = (filterId: PlaceType) => {
        if (dragRef.current.suppressNextClick) {
            dragRef.current.suppressNextClick = false;
            dragRef.current.didDrag = false;
            return;
        }

        onChange(filterId);
    };

    return (
        <div
            ref={listRef}
            className="places-filter-list"
            aria-label="Фильтры мест"
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerEnd}
            onPointerCancel={handlePointerEnd}
        >
            {filters.map((filter) => {
                const isActive = filter.id === activeFilter;
                const style: FilterStyle = { "--filter-color": filter.color };

                return (
                    <button
                        key={filter.id}
                        type="button"
                        data-filter-id={filter.id}
                        className={`places-filter ${isActive ? "places-filter-active" : ""}`}
                        style={style}
                        aria-pressed={isActive}
                        onClick={() => handleClick(filter.id)}
                    >
                        <span className={`places-filter-icon places-filter-icon-${filter.id}`} aria-hidden="true" />
                        {filter.title}
                    </button>
                );
            })}
        </div>
    );
}

type PlaceCardProps = {
    place: MapPlace;
};

function PlaceCard({ place }: PlaceCardProps) {
    return (
        <li className="place-item">
            <div className="place-copy">
                <p className="place-title">
                    {place.title}
                    <span className="place-dot" aria-hidden="true" />
                    <span className={`place-kind place-kind-${place.type}`}>{place.typeLabel}</span>
                </p>
                <p className="place-hours">{place.hours}</p>
                <p className="place-hours">{place.address}</p>

                <div className="place-actions" aria-label={`Действия для ${place.title}`}>
                    {place.website ? (
                        <a
                            className="place-action"
                            aria-label="Открыть сайт"
                            href={place.website}
                            target="_blank"
                            rel="noreferrer"
                        >
                            <GlobeIcon />
                        </a>
                    ) : null}
                    {place.phone ? (
                        <a className="place-action" aria-label="Позвонить" href={`tel:${place.phone}`}>
                            <PhoneIcon />
                        </a>
                    ) : null}
                </div>
            </div>

            <div className={`place-logo place-logo-${place.type}`} aria-hidden="true">
                {place.logo}
            </div>
        </li>
    );
}

export function MapPage() {
    const navigate = useNavigate();
    const clinicsQuery = useClinicsQuery();
    const friendlyQuery = useFriendlyQuery();
    const groomingsQuery = useGroomingsQuery();

    const [activeFilter, setActiveFilter] = useState<PlaceType | "">("");
    const [searchTerm, setSearchTerm] = useState("");
    const [sheetHeight, setSheetHeight] = useState(SHEET_COLLAPSED);
    const [isSheetDragging, setIsSheetDragging] = useState(false);
    const sheetDragRef = useRef<SheetDragState>(initialSheetDrag);

    const allPlaces = useMemo(
        () => [
            ...(clinicsQuery.data?.map(mapClinicToPlace) ?? []),
            ...(friendlyQuery.data?.map(mapDogPlaceToPlace) ?? []),
            ...(groomingsQuery.data?.map(mapGroomingToPlace) ?? []),
        ],
        [clinicsQuery.data, friendlyQuery.data, groomingsQuery.data],
    );

    const visiblePlaces = useMemo(() => {
        const normalizedSearch = searchTerm.trim().toLowerCase();

        return allPlaces.filter((place) => {
            const matchesFilter = !activeFilter || place.type === activeFilter;
            const matchesSearch =
                !normalizedSearch ||
                place.title.toLowerCase().includes(normalizedSearch) ||
                place.address.toLowerCase().includes(normalizedSearch);

            return matchesFilter && matchesSearch;
        });
    }, [activeFilter, allPlaces, searchTerm]);

    const isLoading =
        clinicsQuery.isLoading || friendlyQuery.isLoading || groomingsQuery.isLoading;
    const isError =
        clinicsQuery.isError || friendlyQuery.isError || groomingsQuery.isError;

    const handleSheetPointerDown = (event: PointerEvent<HTMLElement>) => {
        if (shouldIgnoreSheetDrag(event.target)) {
            return;
        }

        sheetDragRef.current = {
            startY: event.clientY,
            startHeight: sheetHeight,
            currentHeight: sheetHeight,
            isDragging: true,
        };
        setIsSheetDragging(true);
        event.currentTarget.setPointerCapture(event.pointerId);
    };

    const handleSheetPointerMove = (event: PointerEvent<HTMLElement>) => {
        const drag = sheetDragRef.current;

        if (!drag.isDragging) {
            return;
        }

        const nextHeight = drag.startHeight + drag.startY - event.clientY;
        const height = clamp(nextHeight, SHEET_COLLAPSED, getMaxSheetHeight());

        drag.currentHeight = height;
        setSheetHeight(height);
    };

    const handleSheetPointerEnd = (event: PointerEvent<HTMLElement>) => {
        const drag = sheetDragRef.current;

        if (!drag.isDragging) {
            return;
        }

        const height = getClosestSheetHeight(drag.currentHeight);

        drag.currentHeight = height;
        drag.isDragging = false;
        setIsSheetDragging(false);
        setSheetHeight(height);
        releasePointerCapture(event.currentTarget, event.pointerId);
    };

        return (
        <div className="map-page">
            <button
                type="button"
                className="map-back-button"
                aria-label="Вернуться на главный экран"
                onClick={() => navigate({ to: appRoutes.home })}
            >
                <svg className="map-back-button-icon" viewBox="0 0 11 18" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                    <path d="M8.91892 18L0 9L8.91892 0L11 2.1L4.16216 9L11 15.9L8.91892 18Z" fill="currentColor"/>
                </svg>
            </button>

            <MapCanvas places={visiblePlaces} />

            <section
                className={`places-sheet ${isSheetDragging ? "places-sheet-dragging" : ""}`}
                style={{ height: `${sheetHeight}px` }}
                aria-label="Места рядом"
                onPointerDown={handleSheetPointerDown}
                onPointerMove={handleSheetPointerMove}
                onPointerUp={handleSheetPointerEnd}
                onPointerCancel={handleSheetPointerEnd}
            >
                <div className="places-sheet-handle" aria-hidden="true" />

                <label className="places-search" data-sheet-no-drag>
                    <span className="places-search-icon" aria-hidden="true" />
                    <input
                        type="search"
                        placeholder="ПОИСК И ВЫБОР МЕСТ"
                        value={searchTerm}
                        onChange={(event) => setSearchTerm(event.target.value)}
                    />
                </label>

                <div data-sheet-no-drag>
                    <PlaceFilters activeFilter={activeFilter} onChange={setActiveFilter} />
                </div>

                <ul className="places-list" data-sheet-no-drag>
                    {isLoading ? <li className="place-item">Загружаем места...</li> : null}
                    {isError ? <li className="place-item">Не удалось загрузить места.</li> : null}
                    {visiblePlaces.map((place) => (
                        <PlaceCard key={place.id} place={place} />
                    ))}
                    {!isLoading && !isError && visiblePlaces.length === 0 ? (
                        <li className="place-item">По вашему запросу ничего не найдено.</li>
                    ) : null}
                </ul>
            </section>
        </div>
    );
}
