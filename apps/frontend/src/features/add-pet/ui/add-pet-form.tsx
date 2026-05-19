import { FormEvent, useEffect, useMemo, useState } from "react";

import { useDogBreedsQuery } from "@/entities/pet/model/pet.queries";
import type { AnimalBreed } from "@/entities/pet/model/pet.types";
import { BreedAutocomplete } from "@/entities/pet/ui/breed-autocomplete";
import { useCreatePet } from "@/features/add-pet/model/use-add-pet";

type CreatePetFormProps = {
    onCreated: () => void;
};

export function CreatePetForm({ onCreated }: CreatePetFormProps) {
    const breedsQuery = useDogBreedsQuery();
    const createPet = useCreatePet();
    const [name, setName] = useState("");
    const [breedQuery, setBreedQuery] = useState("");
    const [breedId, setBreedId] = useState("");
    const [age, setAge] = useState("");
    const [weight, setWeight] = useState("");
    const [sex, setSex] = useState<"male" | "female">("male");
    const [isSterylized, setIsSterylized] = useState(false);
    const [healthNotes, setHealthNotes] = useState("");
    const [photo, setPhoto] = useState<File | null>(null);
    const [breedError, setBreedError] = useState(false);

    const photoPreviewUrl = useMemo(() => {
        if (!photo) {
            return null;
        }

        return URL.createObjectURL(photo);
    }, [photo]);

    useEffect(() => {
        return () => {
            if (photoPreviewUrl) {
                URL.revokeObjectURL(photoPreviewUrl);
            }
        };
    }, [photoPreviewUrl]);

    function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();

        if (!breedId) {
            setBreedError(true);
            return;
        }

        createPet.mutate(
            {
                name: name.trim(),
                breedId: Number(breedId),
                age: Number(age),
                weight: Number(weight),
                sex,
                isSterylized,
                healthNotes,
                photo,
            },
            {
                onSuccess: () => {
                    setName("");
                    setBreedQuery("");
                    setBreedId("");
                    setAge("");
                    setWeight("");
                    setSex("male");
                    setIsSterylized(false);
                    setHealthNotes("");
                    setPhoto(null);
                    setBreedError(false);
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
                <BreedAutocomplete
                    value={breedQuery}
                    onChange={(value) => {
                        setBreedQuery(value);
                        setBreedError(false);
                        setBreedId(findMatchingBreedId(value, breedsQuery.data ?? []));
                    }}
                    onSelect={(breed) => {
                        setBreedQuery(breed.animal_breed);
                        setBreedId(String(breed.id));
                        setBreedError(false);
                    }}
                    breeds={breedsQuery.data ?? []}
                    invalid={breedError}
                    disabled={breedsQuery.isLoading || breedsQuery.isError}
                    placeholder={breedsQuery.isLoading ? "Загружаем породы..." : "Начните вводить породу"}
                    required
                />
            </label>

            {breedError ? (
                <p className="create-pet-error">
                    Выберите породу из предложенного списка.
                </p>
            ) : null}

            <div className="create-pet-grid">
                <label className="create-pet-field">
                    <span>Возраст, лет</span>
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

            <div className="create-pet-field">
                <span>Пол</span>
                <div className="create-pet-sex-toggle" role="group" aria-label="Выбор пола питомца">
                    <button
                        type="button"
                        className={`create-pet-sex-option ${sex === "male" ? "is-active" : ""}`}
                        aria-pressed={sex === "male"}
                        onClick={() => setSex("male")}
                    >
                        самец
                    </button>
                    <button
                        type="button"
                        className={`create-pet-sex-option ${sex === "female" ? "is-active" : ""}`}
                        aria-pressed={sex === "female"}
                        onClick={() => setSex("female")}
                    >
                        самка
                    </button>
                </div>
            </div>

            <div className="create-pet-field">
                <span>Стерилизован(а)</span>
                <div className="create-pet-sex-toggle" role="group" aria-label="Выбор статуса стерилизации питомца">
                    <button
                        type="button"
                        className={`create-pet-sex-option ${isSterylized ? "is-active" : ""}`}
                        aria-pressed={isSterylized}
                        onClick={() => setIsSterylized(true)}
                    >
                        да
                    </button>
                    <button
                        type="button"
                        className={`create-pet-sex-option ${!isSterylized ? "is-active" : ""}`}
                        aria-pressed={!isSterylized}
                        onClick={() => setIsSterylized(false)}
                    >
                        нет
                    </button>
                </div>
            </div>

            <label className="create-pet-field">
                <span>Особенности здоровья питомца</span>
                <textarea
                    className="create-pet-textarea"
                    value={healthNotes}
                    onChange={(event) => setHealthNotes(event.target.value)}
                    maxLength={500}
                    placeholder="Например: аллергия, хронические заболевания, особенности питания, лекарства"
                />
            </label>

            <label className="create-pet-photo">
                {photoPreviewUrl ? (
                    <img src={photoPreviewUrl} alt="" />
                ) : (
                    <span>Выбрать фото</span>
                )}
                <input
                    type="file"
                    accept="image/*"
                    onClick={(event) => {
                        event.currentTarget.value = "";
                    }}
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

function findMatchingBreedId(value: string, breeds: AnimalBreed[]): string {
    const normalizedValue = value.trim().toLowerCase();
    const breed = breeds.find((item) => item.animal_breed.trim().toLowerCase() === normalizedValue);

    return breed ? String(breed.id) : "";
}
