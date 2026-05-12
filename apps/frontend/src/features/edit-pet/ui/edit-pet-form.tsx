import { FormEvent, useEffect, useMemo, useRef, useState } from "react";

import { DEFAULT_ANIMAL_TYPE_ID } from "@/entities/pet/api/animal-reference.api";
import type { AnimalBreed, Pet, PetSex } from "@/entities/pet/model/pet.types";
import { useUpdatePet } from "@/features/edit-pet/model/use-update-pet";
import { useUploadPetPhoto } from "@/features/upload-photo/model/use-upload-pet-photo";

import "./edit-pet-form.css";

type EditPetFormProps = {
    pet: Pet;
    breeds: AnimalBreed[];
    photoUrl: string | null;
    onCancel: () => void;
    onSaved: () => void;
};

const DOG_BREEDS_DATALIST_ID = "edit-pet-dog-breeds";

export function EditPetForm({ pet, breeds, photoUrl, onCancel, onSaved }: EditPetFormProps) {
    const updatePet = useUpdatePet();
    const uploadPetPhoto = useUploadPetPhoto();
    const fileInputRef = useRef<HTMLInputElement | null>(null);

    const currentBreed = useMemo(
        () => breeds.find((breed) => breed.id === pet.animal_breed_id)?.animal_breed ?? "",
        [breeds, pet.animal_breed_id],
    );

    const [name, setName] = useState(pet.pet_name);
    const [breed, setBreed] = useState(currentBreed);
    const [dateOfBirth, setDateOfBirth] = useState(formatDateForView(pet.pet_date_of_birth));
    const [weight, setWeight] = useState(String(pet.pet_weight ?? ""));
    const [sex, setSex] = useState<PetSex | null>(pet.pet_sex ?? null);
    const [isSterylized, setIsSterylized] = useState<boolean | null>(pet.pet_is_sterylyzed ?? null);
    const [features, setFeatures] = useState(pet.pet_special_notes ?? "");
    const [photo, setPhoto] = useState<File | null>(null);
    const [dateError, setDateError] = useState(false);

    const photoPreviewUrl = useMemo(() => {
        if (!photo) {
            return null;
        }

        return URL.createObjectURL(photo);
    }, [photo]);

    useEffect(() => {
        setBreed(currentBreed);
    }, [currentBreed]);

    useEffect(() => {
        return () => {
            if (photoPreviewUrl) {
                URL.revokeObjectURL(photoPreviewUrl);
            }
        };
    }, [photoPreviewUrl]);

    const visiblePhotoUrl = photoPreviewUrl ?? photoUrl;
    const isSubmitting = updatePet.isPending || uploadPetPhoto.isPending;

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();

        const parsedDate = parseDateInput(dateOfBirth);
        if (!parsedDate) {
            setDateError(true);
            return;
        }

        setDateError(false);

        const normalizedBreed = breed.trim().toLowerCase();
        const selectedBreed = breeds.find(
            (item) => item.animal_breed.trim().toLowerCase() === normalizedBreed,
        );

        await updatePet.mutateAsync({
            petId: pet.id,
            payload: {
                pet_name: name.trim(),
                pet_date_of_birth: parsedDate,
                animal_type_id: pet.animal_type_id || DEFAULT_ANIMAL_TYPE_ID,
                animal_breed_id: selectedBreed?.id || undefined,
                animal_breed_name: breed.trim() || undefined,
                pedigree: pet.pedigree,
                pet_weight: Number(weight),
                pet_sex: sex,
                pet_is_sterylyzed: isSterylized,
                pet_special_notes: features.trim() || null,
            },
        });

        if (photo) {
            await uploadPetPhoto.mutateAsync({
                petId: pet.id,
                file: photo,
            });
        }

        onSaved();
    }

    return (
        <form id="edit-pet-form" className="edit-pet-form" onSubmit={handleSubmit}>
            <label className="edit-pet-photo-control">
                <span className="edit-pet-photo-frame">
                    {visiblePhotoUrl ? (
                        <img src={visiblePhotoUrl} alt={name} />
                    ) : (
                        <span className="edit-pet-photo-placeholder">
                            {name.slice(0, 1).toUpperCase() || "?"}
                        </span>
                    )}
                </span>

                <span className="edit-pet-photo-text">изменить фото</span>

                <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={(event) => setPhoto(event.target.files?.[0] ?? null)}
                />
            </label>

            <label className="edit-pet-field edit-pet-field--name">
                <span className="edit-pet-label">Имя</span>
                <input
                    value={name}
                    onChange={(event) => setName(event.target.value)}
                    minLength={2}
                    maxLength={50}
                    required
                />
            </label>

            <label className="edit-pet-field">
                <span className="edit-pet-label">Порода</span>
                <input
                    value={breed}
                    onChange={(event) => setBreed(event.target.value)}
                    list={DOG_BREEDS_DATALIST_ID}
                    maxLength={50}
                    required
                />
                <datalist id={DOG_BREEDS_DATALIST_ID}>
                    {breeds.map((item) => (
                        <option key={item.id} value={item.animal_breed} />
                    ))}
                </datalist>
            </label>

            <div className="edit-pet-grid">
                <label className="edit-pet-field">
                    <span className="edit-pet-label">Дата рождения</span>
                    <input
                        value={dateOfBirth}
                        onChange={(event) => setDateOfBirth(event.target.value)}
                        placeholder="ММ/ДД/ГГГГ"
                        inputMode="numeric"
                        aria-invalid={dateError}
                        required
                    />
                </label>

                <label className="edit-pet-field">
                    <span className="edit-pet-label">Вес, кг</span>
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

            {dateError ? (
                <p className="edit-pet-error edit-pet-error--date">
                    Укажите дату в формате ММ/ДД/ГГГГ.
                </p>
            ) : null}

            <fieldset className="edit-pet-segment-field">
                <legend className="edit-pet-label">Пол</legend>
                <div className="edit-pet-segment">
                    <button
                        type="button"
                        className={sex === "male" ? "edit-pet-segment-button is-active" : "edit-pet-segment-button"}
                        onClick={() => setSex("male")}
                    >
                        самец
                    </button>
                    <button
                        type="button"
                        className={sex === "female" ? "edit-pet-segment-button is-active" : "edit-pet-segment-button"}
                        onClick={() => setSex("female")}
                    >
                        самка
                    </button>
                </div>
            </fieldset>

            <fieldset className="edit-pet-segment-field edit-pet-segment-field--sterilized">
                <legend className="edit-pet-label">Стерилизован(а)</legend>
                <div className="edit-pet-segment">
                    <button
                        type="button"
                        className={isSterylized === true ? "edit-pet-segment-button is-active" : "edit-pet-segment-button"}
                        onClick={() => setIsSterylized(true)}
                    >
                        да
                    </button>
                    <button
                        type="button"
                        className={isSterylized === false ? "edit-pet-segment-button is-active" : "edit-pet-segment-button"}
                        onClick={() => setIsSterylized(false)}
                    >
                        нет
                    </button>
                </div>
            </fieldset>

            <label className="edit-pet-field edit-pet-field--features">
                <span className="edit-pet-label">Особенности</span>
                <input
                    value={features}
                    onChange={(event) => setFeatures(event.target.value)}
                    maxLength={250}
                />
            </label>

            {(updatePet.isError || uploadPetPhoto.isError) ? (
                <p className="edit-pet-error">
                    Не удалось сохранить изменения. Проверьте данные и попробуйте ещё раз.
                </p>
            ) : null}

            <div className="edit-pet-actions">
                <button type="button" className="edit-pet-cancel" onClick={onCancel} disabled={isSubmitting}>
                    Отмена
                </button>
                <button type="submit" className="edit-pet-submit" disabled={isSubmitting}>
                    Добавить
                </button>
            </div>
        </form>
    );
}

function formatDateForView(value: string): string {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "";
    }

    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const year = String(date.getFullYear());

    return `${month}/${day}/${year}`;
}

function parseDateInput(value: string): string | null {
    const trimmedValue = value.trim();

    if (/^\d{4}-\d{2}-\d{2}$/.test(trimmedValue)) {
        return isValidDateString(trimmedValue) ? trimmedValue : null;
    }

    const match = trimmedValue.match(/^(\d{1,2})[./-](\d{1,2})[./-](\d{4})$/);
    if (!match) {
        return null;
    }

    const [, firstPart, secondPart, year] = match;
    const month = Number(firstPart);
    const day = Number(secondPart);
    const isoDate = `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;

    return isValidDateString(isoDate) ? isoDate : null;
}

function isValidDateString(value: string): boolean {
    const date = new Date(`${value}T00:00:00`);

    if (Number.isNaN(date.getTime())) {
        return false;
    }

    return date.toISOString().slice(0, 10) === value;
}