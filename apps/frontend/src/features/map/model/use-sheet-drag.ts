import { useRef, useState } from "react";
import type { PointerEvent } from "react";

const SHEET_COLLAPSED = 164;
const SHEET_HALF = 430;
const SHEET_EXPANDED = 660;
const SHEET_TOP_OFFSET = 72;

type SheetDragState = {
    startY: number;
    startHeight: number;
    currentHeight: number;
    isDragging: boolean;
};

const initialSheetDrag: SheetDragState = {
    startY: 0,
    startHeight: SHEET_HALF,
    currentHeight: SHEET_HALF,
    isDragging: false,
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

function releasePointerCapture(element: Element, pointerId: number) {
    if (element.hasPointerCapture(pointerId)) {
        element.releasePointerCapture(pointerId);
    }
}

export function useSheetDrag(initialHeight = SHEET_COLLAPSED) {
    const [sheetHeight, setSheetHeight] = useState(initialHeight);
    const [isSheetDragging, setIsSheetDragging] = useState(false);
    const sheetDragRef = useRef<SheetDragState>(initialSheetDrag);

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

    return {
        sheetHeight,
        isSheetDragging,
        handleSheetPointerDown,
        handleSheetPointerMove,
        handleSheetPointerEnd,
    };
}
