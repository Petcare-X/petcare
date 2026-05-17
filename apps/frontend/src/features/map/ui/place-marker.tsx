import type { MapPlace } from "@/entities/map-point/model/map.types";

import { ClinicsIcon, FriendlyIcon, GroomingsIcon } from "../lib/map-icons";

type PlaceMarkerProps = {
    place: MapPlace;
};

export function PlaceMarker({ place }: PlaceMarkerProps) {
    return (
        <div
            className={`custom-marker custom-marker-${place.type}`}
            aria-label={place.title}
        >
            <span className="custom-marker-icon">
                {place.type === "place" ? <FriendlyIcon /> : null}
                {place.type === "clinic" ? <ClinicsIcon /> : null}
                {place.type === "salon" ? <GroomingsIcon/> : null}
            </span>
        </div>
    );
}
