import { useEffect, useState } from "react";

export type MapLocation = {
    center: [number, number];
    zoom: number;
};

export const DEFAULT_MAP_LOCATION: MapLocation = {
    center: [39.7015, 47.2357],
    zoom: 11,
};

export function useUserGeolocation(defaultLocation: MapLocation = DEFAULT_MAP_LOCATION) {
    const [mapLocation, setMapLocation] = useState<MapLocation>(defaultLocation);
    const [userCoordinates, setUserCoordinates] = useState<[number, number] | null>(null);

    useEffect(() => {
        if (!("geolocation" in navigator)) {
            return;
        }

        navigator.geolocation.getCurrentPosition(
            ({ coords }) => {
                const coordinates: [number, number] = [coords.longitude, coords.latitude];

                setUserCoordinates(coordinates);
                setMapLocation({
                    center: coordinates,
                    zoom: 12,
                });
            },
            () => {
                setMapLocation(defaultLocation);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000,
            },
        );
    }, [defaultLocation]);

    return {
        mapLocation,
        userCoordinates,
    };
}
