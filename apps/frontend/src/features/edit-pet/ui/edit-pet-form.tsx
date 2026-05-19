import { FormEvent, useEffect, useMemo, useRef, useState } from "react";

import { DEFAULT_ANIMAL_TYPE_ID } from "@/entities/pet/api/animal-reference.api";
import type { UpdatePetPayload } from "@/entities/pet/api/pet.api";
import type { AnimalBreed, Pet, PetSex } from "@/entities/pet/model/pet.types";
import { BreedAutocomplete } from "@/entities/pet/ui/breed-autocomplete";
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

export function EditPetForm({ pet, breeds, photoUrl, onCancel, onSaved }: EditPetFormProps) {
    const updatePet = useUpdatePet();
    const uploadPetPhoto = useUploadPetPhoto();
    const fileInputRef = useRef<HTMLInputElement | null>(null);
    const currentBreed = useMemo(
        () => breeds.find((breed) => breed.id === pet.animal_breed_id)?.animal_breed ?? "",
        [breeds, pet.animal_breed_id],
    );
    const initialDateOfBirth = useMemo(
        () => formatDateForView(pet.pet_date_of_birth),
        [pet.pet_date_of_birth],
    );

    const [name, setName] = useState(pet.pet_name);
    const [breedQuery, setBreedQuery] = useState(currentBreed);
    const [breedId, setBreedId] = useState(String(pet.animal_breed_id ?? ""));
    const [dateOfBirth, setDateOfBirth] = useState(initialDateOfBirth);
    const [weight, setWeight] = useState(String(pet.pet_weight ?? ""));
    const [sex, setSex] = useState<PetSex | undefined>(pet.pet_sex ?? undefined);
    const [isSterylized, setIsSterylized] = useState<boolean | null>(pet.pet_is_sterylyzed ?? null);
    const [features, setFeatures] = useState(pet.pet_special_notes ?? "");
    const [photo, setPhoto] = useState<File | null>(null);
    const [dateError, setDateError] = useState(false);
    const [breedError, setBreedError] = useState(false);

    const photoPreviewUrl = useMemo(() => {
        if (!photo) {
            return null;
        }

        return URL.createObjectURL(photo);
    }, [photo]);

    useEffect(() => {
        setBreedQuery(currentBreed);
        setBreedId(String(pet.animal_breed_id ?? ""));
    }, [currentBreed, pet.animal_breed_id]);

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

        const shouldUpdateDate = dateOfBirth.trim() !== initialDateOfBirth;
        const parsedDate = shouldUpdateDate ? parseDateInput(dateOfBirth) : null;

        if (shouldUpdateDate && !parsedDate) {
            setDateError(true);
            return;
        }

        if (!breedId) {
            setBreedError(true);
            return;
        }

        setDateError(false);
        setBreedError(false);

        const payload: UpdatePetPayload = {
            pet_name: name.trim(),
            animal_type_id: pet.animal_type_id || DEFAULT_ANIMAL_TYPE_ID,
            animal_breed_id: Number(breedId),
            pedigree: pet.pedigree,
            pet_weight: Number(weight),
            pet_sex: sex,
            pet_is_sterylyzed: isSterylized,
            pet_special_notes: features.trim() || null,
        };

        if (parsedDate) {
            payload.pet_date_of_birth = parsedDate;
        }

        await updatePet.mutateAsync({
            petId: pet.id,
            payload,
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
                    onClick={(event) => {
                        event.currentTarget.value = "";
                    }}
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
                <BreedAutocomplete
                    value={breedQuery}
                    onChange={(value) => {
                        setBreedQuery(value);
                        setBreedError(false);
                        setBreedId(findMatchingBreedId(value, breeds));
                    }}
                    onSelect={(breed) => {
                        setBreedQuery(breed.animal_breed);
                        setBreedId(String(breed.id));
                        setBreedError(false);
                    }}
                    breeds={breeds}
                    invalid={breedError}
                    disabled={breeds.length === 0}
                    placeholder={breeds.length === 0 ? "Загружаем породы..." : "Начните вводить породу"}
                    required
                />
            </label>

            {breedError ? (
                <p className="edit-pet-error edit-pet-error--date">
                    Выберите породу из предложенного списка.
                </p>
            ) : null}

            <div className="edit-pet-grid">
                <label className="edit-pet-field">
                    <span className="edit-pet-label">Дата рождения</span>
                    <input
                        value={dateOfBirth}
                        onChange={(event) => {
                            setDateOfBirth(event.target.value);
                            setDateError(false);
                        }}
                        placeholder="ДД.ММ.ГГГГ"
                        inputMode="numeric"
                        aria-invalid={dateError}
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
                    Укажите дату в формате ДД.ММ.ГГГГ.
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
                    Сохранить
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

function formatDateForView(value: string): string {
    const isoDate = value.trim().slice(0, 10);
    const match = isoDate.match(/^(\d{4})-(\d{2})-(\d{2})$/);

    if (!match || !isValidDateString(isoDate)) {
        return "";
    }

    const [, year, month, day] = match;

    return `${day}.${month}.${year}`;
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
    const day = Number(firstPart);
    const month = Number(secondPart);
    const isoDate = `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;

    return isValidDateString(isoDate) ? isoDate : null;
}

function isValidDateString(value: string): boolean {
    const match = value.match(/^(\d{4})-(\d{2})-(\d{2})$/);

    if (!match) {
        return false;
    }

    const [, yearPart, monthPart, dayPart] = match;
    const year = Number(yearPart);
    const month = Number(monthPart);
    const day = Number(dayPart);

    if (month < 1 || month > 12 || day < 1) {
        return false;
    }

    const lastDayOfMonth = new Date(Date.UTC(year, month, 0)).getUTCDate();

    return day <= lastDayOfMonth;
}
