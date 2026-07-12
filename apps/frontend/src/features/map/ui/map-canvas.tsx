import { useEffect, useState } from "react";

import { loadReactifiedYmaps } from "@/shared/lib/ymaps";
import type { MapPlace } from "@/entities/map-point/model/map.types";

import type { MapLocation } from "../model/use-user-geolocation";
import { PawIcon } from "../lib/map-icons";
import { PlaceMarker } from "./place-marker";

type MapCanvasProps = {
    places: MapPlace[];
    location: MapLocation;
    userCoordinates: [number, number] | null;
};

type ReactifiedYmapsModule = Awaited<ReturnType<typeof loadReactifiedYmaps>>;

export function MapCanvas({ places, location, userCoordinates }: MapCanvasProps) {
    const [mapsModule, setMapsModule] = useState<ReactifiedYmapsModule | null>(null);
    const [mapLoadError, setMapLoadError] = useState<string | null>(null);

    useEffect(() => {
        let cancelled = false;

        void loadReactifiedYmaps()
            .then((module) => {
                if (cancelled) {
                    return;
                }

                setMapsModule(module);
                setMapLoadError(null);
            })
            .catch((error: unknown) => {
                if (cancelled) {
                    return;
                }

                setMapLoadError(
                    error instanceof Error
                        ? error.message
                        : "Не удалось подключить сервис карт.",
                );
            });

        return () => {
            cancelled = true;
        };
    }, []);

    if (mapLoadError) {
        return (
            <section className="map-service-state" aria-live="polite">
                <div className="map-service-card">
                    <p className="map-service-title">Карта временно недоступна</p>
                    <p className="map-service-description">
                        Не удалось подключить сервис карт. Попробуйте обновить страницу позже.
                    </p>
                </div>
            </section>
        );
    }

    if (!mapsModule) {
        return (
            <section className="map-service-state" aria-live="polite">
                <div className="map-service-card">
                    <p className="map-service-title">Загружаем карту</p>
                    <p className="map-service-description">
                        Подключаем сервис карт и подготавливаем отображение мест.
                    </p>
                </div>
            </section>
        );
    }

    const {
        YMap,
        YMapDefaultSchemeLayer,
        YMapDefaultFeaturesLayer,
        YMapMarker,
    } = mapsModule;

    return (
        <div className="map-stage">
            <YMap location={location}>
                <YMapDefaultSchemeLayer />
                <YMapDefaultFeaturesLayer />

                {userCoordinates ? (
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
                        <PlaceMarker place={place} />
                    </YMapMarker>
                ))}
            </YMap>
        </div>
    );
}
