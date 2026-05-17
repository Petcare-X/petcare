import { YMap, YMapDefaultFeaturesLayer, YMapDefaultSchemeLayer, YMapMarker } from "@/shared/lib/ymaps";
import type { MapPlace } from "@/entities/map-point/model/map.types";

import type { MapLocation } from "../model/use-user-geolocation";
import { PawIcon } from "../lib/map-icons";
import { PlaceMarker } from "./place-marker";

type MapCanvasProps = {
    places: MapPlace[];
    location: MapLocation;
    userCoordinates: [number, number] | null;
};

export function MapCanvas({ places, location, userCoordinates }: MapCanvasProps) {
    return (
        <YMap location={location}>
            <YMapDefaultSchemeLayer />
            <YMapDefaultFeaturesLayer />

            {userCoordinates ?(
                <YMapMarker coordinates={userCoordinates}>
                    <div className="user-location-marker">
                        <PawIcon />
                    </div>
                </YMapMarker>
            ) : null}

            {places.map((place) => (
                <YMapMarker
                    key={`${place.type}-${place.id}`}
                    coordinates={place.coordinates}
                >
                    <PlaceMarker place={place}/>
                </YMapMarker>
            ))}
        </YMap>
    );
}
