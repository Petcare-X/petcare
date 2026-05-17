import { useRef } from "react";
import type { CSSProperties, PointerEvent } from "react";

import type { PlaceType } from "@/entities/map-point/model/map.types";

const filters: PlaceFilter[] = [
    { id: "clinic", title: "Клиники", color: "#d34b1c" },
    { id: "place", title: "Места", color: "#49aa35" },
    { id: "salon", title: "Салоны", color: "#7c83ff" },
];

type PlaceFilter = {
    id: PlaceType;
    title: string;
    color: string;
};

type FilterStyle = CSSProperties & {
    "--filter-color": string;
};

type PlaceFiltersProps = {
    activeFilter: PlaceType | "";
    onChange: (filter: PlaceType) => void;
};

const FILTER_DRAG_THRESHOLD = 8;

type FilterDragState = {
    startX: number;
    startY: number;
    startScrollLeft: number;
    isDragging: boolean;
    didDrag: boolean;
    suppressNextClick: boolean;
    pressedFilterId: PlaceType | null;
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

function getFilterIdFromTarget(target: EventTarget) {
    const button = (target as HTMLElement).closest<HTMLButtonElement>("[data-filter-id]");

    return (button?.dataset.filterId as PlaceType | undefined) ?? null;
}

function releasePointerCapture(element: Element, pointerId: number) {
    if (element.hasPointerCapture(pointerId)) {
        element.releasePointerCapture(pointerId);
    }
}

export function PlaceFilters({ activeFilter, onChange }: PlaceFiltersProps) {
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
