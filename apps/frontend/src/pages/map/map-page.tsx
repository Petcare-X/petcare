import { useNavigate } from "@tanstack/react-router";

import "./map-page.css";
import { appRoutes } from "@/shared/constants/routes";
import { useMapPageData } from "@/features/map/model/use-map-page-data";
import { useSheetDrag } from "@/features/map/model/use-sheet-drag";
import { useUserGeolocation } from "@/features/map/model/use-user-geolocation";
import { MapCanvas } from "@/features/map/ui/map-canvas";
import { PlacesSheet } from "@/features/map/ui/places-sheet";

import { mapRoute } from "@/app/router/routes";

export function MapPage() {
    const search = mapRoute.useSearch() as { filter?: "clinic" | "place" | "salon"};
    const initialFilter = search.filter ?? "";
    
    const navigate = useNavigate();
    const {
        activeFilter,
        searchTerm,
        setSearchTerm,
        visiblePlaces,
        isLoading,
        isError,
        handleFilterChange,
    } = useMapPageData(initialFilter);
    const { mapLocation, userCoordinates } = useUserGeolocation();
    const {
        sheetHeight,
        isSheetDragging,
        handleSheetPointerDown,
        handleSheetPointerMove,
        handleSheetPointerEnd,
    } = useSheetDrag();

    return (
        <main className="map-page">
            <button
                type="button"
                className="map-back-button"
                aria-label="Вернуться на главный экран"
                onClick={() => navigate({ to: appRoutes.home })}
            >
                <svg className="map-back-button-icon" viewBox="0 0 11 18" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                    <path d="M8.91892 18L0 9L8.91892 0L11 2.1L4.16216 9L11 15.9L8.91892 18Z" fill="currentColor" />
                </svg>
            </button>

            <MapCanvas places={visiblePlaces} location={mapLocation} userCoordinates={userCoordinates} />

            <PlacesSheet
                activeFilter={activeFilter}
                searchTerm={searchTerm}
                places={visiblePlaces}
                isLoading={isLoading}
                isError={isError}
                height={sheetHeight}
                isDragging={isSheetDragging}
                onSearchChange={setSearchTerm}
                onFilterChange={handleFilterChange}
                onPointerDown={handleSheetPointerDown}
                onPointerMove={handleSheetPointerMove}
                onPointerUp={handleSheetPointerEnd}
                onPointerCancel={handleSheetPointerEnd}
            />
        </main>
    );
}
