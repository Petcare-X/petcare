import { FormEvent, useMemo, useState } from "react";

import { useDogBreedsQuery } from "@/entities/pet/model/pet.queries";
import { useCreatePet } from "@/features/create-pet/model/use-create-pet";

type CreatePetFormProps = {
    onCreated: () => void;
};

export function CreatePetForm({ onCreated }: CreatePetFormProps) {
    const breedsQuery = useDogBreedsQuery();
    const createPet = useCreatePet();
    const [name, setName] = useState("");
    const [breed, setBreed] = useState("");
    const [age, setAge] = useState("");
    const [weight, setWeight] = useState("");
    const [photo, setPhoto] = useState<File | null>(null);

    const photoPreviewUrl = useMemo(() => {
        if (!photo) {
            return null;
        }

        return URL.createObjectURL(photo);
    }, [photo]);

    function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();

        createPet.mutate(
            {
                name: name.trim(),
                breed: breed.trim(),
                age: Number(age),
                weight: Number(weight),
                photo,
            },
            {
                onSuccess: () => {
                    setName("");
                    setBreed("");
                    setAge("");
                    setWeight("");
                    setPhoto(null);
                    onCreated();
                },
            },
        );
    }

    return (
        <form className="create-pet-form" onSubmit={handleSubmit}>
            <label className="create-pet-field">
                <span>Имя</span>
                <input
                    value={name}
                    onChange={(event) => setName(event.target.value)}
                    minLength={2}
                    maxLength={50}
                    required
                />
            </label>

            <label className="create-pet-field">
                <span>Порода</span>
                <input
                    value={breed}
                    onChange={(event) => setBreed(event.target.value)}
                    list="dog-breeds"
                    maxLength={50}
                    required
                />
                <datalist id="dog-breeds">
                    {breedsQuery.data?.map((item) => (
                        <option key={item.id} value={item.animal_breed} />
                    ))}
                </datalist>
            </label>

            <div className="create-pet-grid">
                <label className="create-pet-field">
                    <span>Возраст</span>
                    <input
                        value={age}
                        onChange={(event) => setAge(event.target.value)}
                        type="number"
                        min="0"
                        max="40"
                        required
                    />
                </label>

                <label className="create-pet-field">
                    <span>Вес, кг</span>
                    <input
                        value={weight}
                        onChange={(event) => setWeight(event.target.value)}
                        type="number"
                        min="0.2"
                        max="200"
                        step="0.1"
                        required
                    />
                </label>
            </div>

            <label className="create-pet-photo">
                {photoPreviewUrl ? (
                    <img src={photoPreviewUrl} alt="" />
                ) : (
                    <span>Выбрать фото</span>
                )}
                <input
                    type="file"
                    accept="image/*"
                    onChange={(event) => setPhoto(event.target.files?.[0] ?? null)}
                />
            </label>

            {createPet.isError ? (
                <p className="create-pet-error">
                    Не удалось добавить питомца. Проверьте данные и попробуйте еще раз.
                </p>
            ) : null}

            <div className="create-pet-actions">
                <button type="button" onClick={onCreated}>
                    Отмена
                </button>
                <button type="submit" disabled={createPet.isPending}>
                    {createPet.isPending ? "Добавляем..." : "Добавить"}
                </button>
            </div>
        </form>
    );
}
