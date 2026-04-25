import { useParams } from "@tanstack/react-router";

export function PetDetailsPage() {
    const { petId } = useParams({ strict: false }) as { petId?: string };

    return (
        <main className="pet-details-page">
            <h1>Профиль питомца</h1>
            <p>Питомец #{petId}</p>
        </main>
    );
}
