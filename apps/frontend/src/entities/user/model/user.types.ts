export type User = {
    id: string;
    user_name: string;
    user_email: string;
    user_phone_number: string;
    user_date_of_birth: string;
    user_photo: string | null;
    telegram_id: number | null;
    auth_provider: string | null;
}