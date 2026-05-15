import { useMemo, useState } from "react";

import { useClinicsQuery, useFriendlyQuery, useGroomingsQuery } from "@/entities/map-point/model/map.queries";
import { mapClinicToPlace, mapDogPlaceToPlace, mapGroomingToPlace, type PlaceType } from "@/entities/map-point/model/map.types";

import { useMapSearch } from "./use-map-search";

export function useMapPageData() {
    const clinicsQuery = useClinicsQuery();
    const friendlyQuery = useFriendlyQuery();
    const groomingsQuery = useGroomingsQuery();

    const [activeFilter, setActiveFilter] = useState<PlaceType | "">("");
    const [searchTerm, setSearchTerm] = useState("");

    const allPlaces = useMemo(
        () => [
            ...(clinicsQuery.data?.map(mapClinicToPlace) ?? []),
            ...(friendlyQuery.data?.map(mapDogPlaceToPlace) ?? []),
            ...(groomingsQuery.data?.map(mapGroomingToPlace) ?? []),
        ],
        [clinicsQuery.data, friendlyQuery.data, groomingsQuery.data],
    );

    const visiblePlaces = useMapSearch(allPlaces, activeFilter, searchTerm);

    const isLoading =
        clinicsQuery.isLoading || friendlyQuery.isLoading || groomingsQuery.isLoading;
    const isError =
        clinicsQuery.isError || friendlyQuery.isError || groomingsQuery.isError;

    const handleFilterChange = (filter: PlaceType) => {
        setActiveFilter((current) => (current === filter ? "" : filter));
    };

    return {
        activeFilter,
        searchTerm,
        setSearchTerm,
        visiblePlaces,
        isLoading,
        isError,
        handleFilterChange,
    };
}
