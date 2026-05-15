import type { PointerEvent } from "react";

import type { MapPlace, PlaceType } from "@/entities/map-point/model/map.types";

import { PlaceCard } from "./place-card";
import { PlaceFilters } from "./places-filters";

type PlacesSheetProps = {
    activeFilter: PlaceType | "";
    searchTerm: string;
    places: MapPlace[];
    isLoading: boolean;
    isError: boolean;
    height: number;
    isDragging: boolean;
    onSearchChange: (value: string) => void;
    onFilterChange: (filter: PlaceType) => void;
    onPointerDown: (event: PointerEvent<HTMLElement>) => void;
    onPointerMove: (event: PointerEvent<HTMLElement>) => void;
    onPointerUp: (event: PointerEvent<HTMLElement>) => void;
    onPointerCancel: (event: PointerEvent<HTMLElement>) => void;
};

export function PlacesSheet({
    activeFilter,
    searchTerm,
    places,
    isLoading,
    isError,
    height,
    isDragging,
    onSearchChange,
    onFilterChange,
    onPointerDown,
    onPointerMove,
    onPointerUp,
    onPointerCancel,
}: PlacesSheetProps) {
    return (
        <section
            className={`places-sheet ${isDragging ? "places-sheet-dragging" : ""}`}
            style={{ height: `${height}px` }}
            aria-label="Места рядом"
            onPointerDown={onPointerDown}
            onPointerMove={onPointerMove}
            onPointerUp={onPointerUp}
            onPointerCancel={onPointerCancel}
        >
            <div className="places-sheet-handle" aria-hidden="true" />

            <label className="places-search" data-sheet-no-drag>
                <span className="places-search-icon" aria-hidden="true" />
                <input
                    type="search"
                    placeholder="ПОИСК И ВЫБОР МЕСТ"
                    value={searchTerm}
                    onChange={(event) => onSearchChange(event.target.value)}
                />
            </label>

            <div data-sheet-no-drag>
                <PlaceFilters activeFilter={activeFilter} onChange={onFilterChange} />
            </div>

            <ul className="places-list" data-sheet-no-drag>
                {isLoading ? <li className="place-item">Загружаем места...</li> : null}
                {isError ? <li className="place-item">Не удалось загрузить места.</li> : null}
                {places.map((place) => (
                    <PlaceCard key={`${place.type}-${place.id}`} place={place} />
                ))}
                {!isLoading && !isError && places.length === 0 ? (
                    <li className="place-item">По вашему запросу ничего не найдено.</li>
                ) : null}
            </ul>
        </section>
    );
}
