import type { MapPlace, PlaceType } from "@/entities/map-point/model/map.types";

export function normalizeSearchValue(value: string) {
    return value
        .toLowerCase()
        .replaceAll("ё", "е")
        .trim();
}

function tokenizeSearchValue(value: string) {
    return normalizeSearchValue(value)
        .split(/\s+/)
        .filter(Boolean);
}

function getPlaceSearchScore(place: MapPlace, search: string, searchTokens: string[]) {
    const title = normalizeSearchValue(place.title);
    const titleWords = title.split(/\s+/).filter(Boolean);

    if (!searchTokens.every((token) => title.includes(token))) {
        return 0;
    }

    if (title === search) return 500;
    if (title.startsWith(search)) return 400;
    if (titleWords.some((word) => word.startsWith(search))) return 300;
    if (searchTokens.every((token) => titleWords.some((word) => word.startsWith(token)))) return 250;
    if (title.includes(search)) return 200;

    return 0;
}

export function getVisiblePlaces(
    places: MapPlace[],
    activeFilter: PlaceType | "",
    searchTerm: string,
) {
    const normalizedSearch = normalizeSearchValue(searchTerm);
    const searchTokens = tokenizeSearchValue(searchTerm);
    const filteredByType = places.filter(
        (place) => !activeFilter || place.type === activeFilter,
    );

    if (!normalizedSearch) {
        return filteredByType;
    }

    return filteredByType
        .map((place) => ({
            place,
            score: getPlaceSearchScore(place, normalizedSearch, searchTokens),
        }))
        .filter(({ score }) => score > 0)
        .sort((a, b) => b.score - a.score || a.place.title.localeCompare(b.place.title, "ru"))
        .map(({ place }) => place);
}
