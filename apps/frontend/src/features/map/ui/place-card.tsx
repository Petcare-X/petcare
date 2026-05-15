import type { MapPlace } from "@/entities/map-point/model/map.types";

import { GlobeIcon, PhoneIcon } from "../lib/map-icons";

type PlaceCardProps = {
    place: MapPlace;
};

export function PlaceCard({ place }: PlaceCardProps) {
    return (
        <li className="place-item">
            <div className="place-copy">
                <p className="place-title">
                    {place.title}
                    <span className="place-dot" aria-hidden="true" />
                    <span className={`place-kind place-kind-${place.type}`}>{place.typeLabel}</span>
                </p>
                <p className="place-hours">{place.hours}</p>
                <p className="place-hours">{place.address}</p>

                <div className="place-actions" aria-label={`Действия для ${place.title}`}>
                    {place.website ? (
                        <a
                            className="place-action"
                            aria-label="Открыть сайт"
                            href={place.website}
                            target="_blank"
                            rel="noreferrer"
                        >
                            <GlobeIcon />
                        </a>
                    ) : null}
                    {place.phone ? (
                        <a className="place-action" aria-label="Позвонить" href={`tel:${place.phone}`}>
                            <PhoneIcon />
                        </a>
                    ) : null}
                </div>
            </div>

            <div className={`place-logo place-logo-${place.type}`} aria-hidden="true">
                {place.logo}
            </div>
        </li>
    );
}
