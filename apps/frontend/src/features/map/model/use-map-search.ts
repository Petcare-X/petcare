import { useMemo } from "react";

import type { MapPlace, PlaceType } from "@/entities/map-point/model/map.types";

import { getVisiblePlaces } from "./map-search";

export function useMapSearch(
    places: MapPlace[],
    activeFilter: PlaceType | "",
    searchTerm: string,
) {
    return useMemo(
        () => getVisiblePlaces(places, activeFilter, searchTerm),
        [activeFilter, places, searchTerm],
    );
}
