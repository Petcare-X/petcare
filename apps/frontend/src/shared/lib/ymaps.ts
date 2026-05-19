import * as React from "react";
import * as ReactDOM from "react-dom";

import { loadYmaps3 } from "./loadYmaps3";

type ReactifiedYmapsModule = {
    YMap: React.ComponentType<any>;
    YMapDefaultSchemeLayer: React.ComponentType<any>;
    YMapDefaultFeaturesLayer: React.ComponentType<any>;
    YMapMarker: React.ComponentType<any>;
};

let reactifiedYmapsPromise: Promise<ReactifiedYmapsModule> | null = null;

export function loadReactifiedYmaps(): Promise<ReactifiedYmapsModule> {
    if (!reactifiedYmapsPromise) {
        reactifiedYmapsPromise = (async () => {
            const maps = await loadYmaps3();
            const ymaps3React = await maps.import("@yandex/ymaps3-reactify");
            const reactify = ymaps3React.reactify.bindTo(React, ReactDOM);

            return reactify.module(maps) as ReactifiedYmapsModule;
        })().catch((error) => {
            reactifiedYmapsPromise = null;
            throw error;
        });
    }

    return reactifiedYmapsPromise;
}
