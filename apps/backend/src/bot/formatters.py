def format_profile_message(
    *,
    user_name: str,
    pet_names: list[str],
    shared_pet_names: list[str],
) -> str:
    pets_lines = [f"* {pet_name.capitalize()}" for pet_name in pet_names] or ["Питомцев пока нет."]
    shared_lines = [f"* {pet_name.capitalize()}" for pet_name in shared_pet_names] or ["Доступных питомцев пока нет."]
    return "\n".join(
        [
            f"Имя пользователя: {user_name}",
            "",
            "Ваши питомцы:",
            *pets_lines,
            "",
            "Питомцы с доступом:",
            *shared_lines,
        ]
    )


def format_pet_details_message(pet, animal_type_name: str, animal_breed_name: str) -> str:
    return "\n".join(
        [
            f"Кличка: {pet.pet_name}",
            f"Дата рождения: {pet.pet_date_of_birth}",
            f"Тип животного: {animal_type_name}",
            f"Порода: {animal_breed_name}",
            f"Родословная: {'Да' if pet.pedigree else 'Нет'}",
            f"Обхват шеи: {pet.pet_neck_girth} см",
            f"Обхват груди: {pet.pet_breast_girth} см",
            f"Длина: {pet.pet_length} см",
            f"Вес: {pet.pet_weight} кг",
            f"Стерилизован: {'Да' if pet.pet_is_sterylyzed else 'Нет'}",
        ]
    )
