from aiogram.fsm.state import State, StatesGroup


class AddPetStates(StatesGroup):
    pet_name = State()
    pet_date_of_birth = State()
    animal_type_id = State()
    animal_breed_id = State()
    pedigree = State()
    pet_neck_girth = State()
    pet_breast_girth = State()
    pet_length = State()
    pet_weight = State()
    pet_is_sterylyzed = State()
    pet_photo_object_key = State()


class AcceptInviteStates(StatesGroup):
    invite_code = State()


class RevokeAccessStates(StatesGroup):
    shared_user = State()


class UpdatePetPhotoStates(StatesGroup):
    photo = State()


class AddPetDocumentStates(StatesGroup):
    document_type_id = State()
    file = State()


class DeletePetDocumentStates(StatesGroup):
    document_row_id = State()
