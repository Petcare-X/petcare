"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-03-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users_info',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_name', sa.String(50), nullable=False),
        sa.Column('user_date_of_birth', sa.Date(), nullable=False),
        sa.Column('user_email', sa.String(50), unique=True, nullable=False),
        sa.Column('user_password_hash', sa.Text(), nullable=False),
        sa.Column('user_phone', sa.String(16), unique=True, nullable=False),
        sa.Column('user_photo', sa.Text(), nullable=False),
    )
    op.create_index('ix_users_info_email', 'users_info', ['user_email'])
    op.create_index('ix_users_info_phone', 'users_info', ['user_phone'])

    # Animal types
    op.create_table(
        'animals_types',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('animal_name', sa.String(50), unique=True, nullable=False),
    )

    # Animal breeds
    op.create_table(
        'animals_breeds',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('animal_breed_name', sa.String(50), unique=True, nullable=False),
    )

    # Animal pedigrees
    op.create_table(
        'animals_pedigrees',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('animal_pedigree', sa.String(50), unique=True, nullable=False),
    )

    # Pets table
    op.create_table(
        'pets_info',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users_info.id', ondelete='CASCADE'), nullable=True),
        sa.Column('pet_date_of_birth', sa.Date(), nullable=False),
        sa.Column('pet_type', sa.Integer(), sa.ForeignKey('animals_types.id', ondelete='CASCADE'), nullable=False),
        sa.Column('pet_breed', sa.Integer(), sa.ForeignKey('animals_breeds.id', ondelete='CASCADE'), nullable=False),
        sa.Column('pet_pedigree', sa.Integer(), sa.ForeignKey('animals_pedigrees.id', ondelete='CASCADE'), nullable=True),
        sa.Column('pet_neck_girth', sa.Numeric(10, 2), nullable=True),
        sa.Column('pet_breast_girth', sa.Numeric(10, 2), nullable=True),
        sa.Column('pet_length', sa.Numeric(10, 2), nullable=True),
        sa.Column('pet_is_sterilized', sa.Boolean(), nullable=True),
        sa.Column('pet_photo', sa.Text(), nullable=False),
    )

    # Document types
    op.create_table(
        'documents_types',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('document_name', sa.String(50), unique=True, nullable=False),
    )

    # Pet documents
    op.create_table(
        'pet_documents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('pet_id', sa.Integer(), sa.ForeignKey('pets_info.id', ondelete='CASCADE'), nullable=False),
        sa.Column('document_id', sa.Integer(), sa.ForeignKey('documents_types.id', ondelete='CASCADE'), nullable=False),
    )

    # Vet clinics
    op.create_table(
        'vet_clinics',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('vet_clinic_name', sa.String(100), nullable=False),
        sa.Column('vet_clinic_address', sa.String(200), nullable=False),
        sa.Column('vet_clinic_rating', sa.Numeric(3, 2), nullable=True),
        sa.Column('vet_clinic_work_hours', sa.String(100), nullable=False),
        sa.Column('vet_clinic_contacts', sa.String(100), nullable=False),
        sa.Column('vet_clinic_description', sa.Text(), nullable=True),
        sa.Column('vet_clinic_photo', sa.Text(), nullable=True),
    )

    # Dog friendly places
    op.create_table(
        'dog_friendly_places',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('dogfriendly_place_name', sa.String(100), nullable=False),
        sa.Column('dogfriendly_place_address', sa.String(200), nullable=False),
        sa.Column('dogfriendly_place_rating', sa.Numeric(3, 2), nullable=True),
        sa.Column('dogfriendly_place_work_hours', sa.String(100), nullable=False),
        sa.Column('dogfriendly_place_contacts', sa.String(100), nullable=False),
        sa.Column('dogfriendly_place_description', sa.Text(), nullable=True),
        sa.Column('dogfriendly_place_photo', sa.Text(), nullable=True),
    )

    # Suitable vet clinics
    op.create_table(
        'suitable_vet_clinics',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('pet_id', sa.Integer(), sa.ForeignKey('pets_info.id', ondelete='CASCADE'), nullable=False),
        sa.Column('clinic_id', sa.Integer(), sa.ForeignKey('vet_clinics.id', ondelete='CASCADE'), nullable=False),
    )

    # Suitable dog friendly places
    op.create_table(
        'suitable_dogfriendly_places',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('pet_id', sa.Integer(), sa.ForeignKey('pets_info.id', ondelete='CASCADE'), nullable=False),
        sa.Column('place_id', sa.Integer(), sa.ForeignKey('dog_friendly_places.id', ondelete='CASCADE'), nullable=False),
    )

    # Shared users
    op.create_table(
        'shared_users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('shared_with_user_id', sa.Integer(), sa.ForeignKey('users_info.id', ondelete='CASCADE'), nullable=False),
        sa.Column('pet_id', sa.Integer(), sa.ForeignKey('pets_info.id', ondelete='CASCADE'), nullable=False),
        sa.Column('shared_till', sa.DateTime(timezone=True), nullable=False),
        sa.Column('has_shared_pet', sa.Boolean(), nullable=True),
    )

    # Smart diets
    op.create_table(
        'smart_diets',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('pet_id', sa.Integer(), sa.ForeignKey('pets_info.id', ondelete='CASCADE'), nullable=False),
        sa.Column('food_photo', sa.Text(), nullable=True),
        sa.Column('calculated_food_norm', sa.String(50), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('smart_diets')
    op.drop_table('shared_users')
    op.drop_table('suitable_dogfriendly_places')
    op.drop_table('suitable_vet_clinics')
    op.drop_table('dog_friendly_places')
    op.drop_table('vet_clinics')
    op.drop_table('pet_documents')
    op.drop_table('documents_types')
    op.drop_table('pets_info')
    op.drop_table('animals_pedigrees')
    op.drop_table('animals_breeds')
    op.drop_table('animals_types')
    op.drop_table('users_info')