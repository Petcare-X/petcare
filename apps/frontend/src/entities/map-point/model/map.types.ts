export type PlaceType = "clinic" | "place" | "salon";

export type MapPlace = {
    id: number;
    title: string;
    type: PlaceType;
    typeLabel: string;
    hours: string;
    address: string;
    phone: string | null;
    website: string | null;
    coordinates: [number, number];
    logo: string;
};

export type VetClinic = {
    id: number;
    vet_name: string;
    vet_lat: number;
    vet_lon: number;
    vet_working_hours: string;
    vet_is_24_7: string;
    vet_street: string;
    vet_building_number: string;
    vet_phone: string | null;
}

export type DogFriendlyPlace = {
    id: number;
    dogfriendly_place_name: string;
    dogfriendly_place_lat: number;
    dogfriendly_place_lon: number;
    dogfriendly_place_working_hours: string;
    dogfriendly_place_street: string;
    dogfriendly_place_building_number: string;
}

export type Grooming = {
    id: number
    salon_name: string
    salon_lat: number
    salon_lon: number
    salon_working_hours: string
    salon_street: string
    salon_building_number: string;
    salon_phone: string;
    salon_website: string | null;
}

function buildLogo(name: string) {
    return name.slice(0, 2).toUpperCase();
}

export function mapClinicToPlace(clinic: VetClinic): MapPlace {
    return {
        id: clinic.id,
        title: clinic.vet_name,
        type: "clinic",
        typeLabel: "клиника",
        hours: clinic.vet_is_24_7 === "true"
            ? "Круглосуточно"
            : clinic.vet_working_hours,
        address: `${clinic.vet_street}, ${clinic.vet_building_number}`,
        phone: clinic.vet_phone,
        website: null,
        coordinates: [clinic.vet_lon, clinic.vet_lat],
        logo: buildLogo(clinic.vet_name),
    };
}

export function mapDogPlaceToPlace(place: DogFriendlyPlace): MapPlace {
    return {
        id: place.id,
        title: place.dogfriendly_place_name,
        type: "place",
        typeLabel: "дог-френдли",
        hours: place.dogfriendly_place_working_hours,
        address: `${place.dogfriendly_place_street}, ${place.dogfriendly_place_building_number}`,
        phone: null,
        website: null,
        coordinates: [place.dogfriendly_place_lon, place.dogfriendly_place_lat],
        logo: buildLogo(place.dogfriendly_place_name),
    };
}

export function mapGroomingToPlace(salon: Grooming): MapPlace {
    return {
        id: salon.id,
        title: salon.salon_name,
        type: "salon",
        typeLabel: "салон",
        hours: salon.salon_working_hours,
        address: `${salon.salon_street}, ${salon.salon_building_number}`,
        phone: salon.salon_phone,
        website: salon.salon_website,
        coordinates: [salon.salon_lon, salon.salon_lat],
        logo: buildLogo(salon.salon_name),
    };
}