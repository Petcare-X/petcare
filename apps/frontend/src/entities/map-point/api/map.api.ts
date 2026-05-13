import { apiClient } from "@/shared/api/client";
import type { VetClinic, DogFriendlyPlace, Grooming } from "../model/map.types";

export async function getClinics(): Promise<VetClinic[]>  {
    const response = await apiClient.get("/map-points/vet-clinics");
    return response.data;
}

export async function getFriendly(): Promise<DogFriendlyPlace[]> {
    const response = await apiClient.get("/map-points/dogfriendly-places");
    return response.data;
}

export async function getGroomings(): Promise<Grooming[]> {
    const response = await apiClient.get("/map-points/grooming-salons");
    return response.data;
}