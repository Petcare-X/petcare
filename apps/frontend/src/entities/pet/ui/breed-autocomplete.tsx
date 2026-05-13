import { useMemo, useState } from "react";

import type { AnimalBreed } from "@/entities/pet/model/pet.types";

import "./breed-autocomplete.css";

type BreedAutocompleteProps = {
    breeds: AnimalBreed[];
    value: string;
    disabled?: boolean;
    invalid?: boolean;
    placeholder?: string;
    required?: boolean;
    onChange: (value: string) => void;
    onSelect: (breed: AnimalBreed) => void;
};

export function BreedAutocomplete({
    breeds,
    value,
    disabled = false,
    invalid = false,
    placeholder,
    required = false,
    onChange,
    onSelect,
}: BreedAutocompleteProps) {
    const [isOpen, setIsOpen] = useState(false);
    const normalizedValue = normalizeBreedQuery(value);

    const filteredBreeds = useMemo(() => {
        const matchingBreeds = normalizedValue ?
            breeds.filter((breed) => normalizeBreedQuery(breed.animal_breed).includes(normalizedValue)) :
            breeds;

        return matchingBreeds.slice(0, Infinity);
    }, [breeds, normalizedValue]);

    const showDropdown = isOpen && !disabled;
    const showEmptyState = showDropdown && normalizedValue.length > 0 && filteredBreeds.length === 0;

    return (
        <div className="breed-autocomplete">
            <input
                value={value}
                onChange={(event) => {
                    onChange(event.target.value);
                    setIsOpen(true);
                }}
                onFocus={() => setIsOpen(true)}
                onBlur={() => {
                    window.setTimeout(() => setIsOpen(false), 100);
                }}
                placeholder={placeholder}
                autoComplete="off"
                aria-invalid={invalid}
                aria-expanded={showDropdown}
                disabled={disabled}
                required={required}
            />

            {showDropdown ? (
                <div className="breed-autocomplete-popover">
                    {filteredBreeds.length > 0 ? (
                        <ul className="breed-autocomplete-list" role="listbox">
                            {filteredBreeds.map((breed) => (
                                <li key={breed.id}>
                                    <button
                                        type="button"
                                        className="breed-autocomplete-option"
                                        onMouseDown={(event) => {
                                            event.preventDefault();
                                            onSelect(breed);
                                            setIsOpen(false);
                                        }}
                                    >
                                        {breed.animal_breed}
                                    </button>
                                </li>
                            ))}
                        </ul>
                    ) : null}

                    {showEmptyState ? (
                        <p className="breed-autocomplete-empty">
                            Подходящих пород не найдено.
                        </p>
                    ) : null}
                </div>
            ) : null}
        </div>
    );
}

function normalizeBreedQuery(value: string): string {
    return value.trim().toLowerCase();
}
