import { useEffect, useState, type ChangeEvent } from "react";

import { useDeleteAccount } from "@/features/delete-user/model/use-delete-user";
import { useUserQueries } from "@/entities/user/model/user.queries";
import type { User } from "@/entities/user/model/user.types";

import "../profile/profile-page.css"
import "./edit-profile-form.css"


export function EditProfilePage() {
    const userQuery = useUserQueries();

    const deleteUserMutation = useDeleteAccount();

    if (userQuery.isLoading) {
        return <p>Загружаем данные пользователя...</p>;
    }

    if (userQuery.isError || !userQuery.data) {
        return <p>Не удалось загрузить данные пользователя</p>;
    }

    const handleDeleteAccount = async () => {
        const confirmed = window.confirm(
            "Удалить аккаунт? Будут удалены питомцы, документы, фото и история чатов."
        );

        if (!confirmed) {
            return;
        }

        try {
            await deleteUserMutation.mutateAsync();
        } catch (error) {
            console.error("failed to delete account", error);
        }
    };
    

    return (
        <>
            <EditProfileForm user={userQuery.data} />

            <button
                className="delete-user-button"
                type="button"
                onClick={() => void handleDeleteAccount()}
                disabled={deleteUserMutation.isPending}
            >
                {deleteUserMutation.isPending ? "Удаляем..." : "Удалить аккаунт"}
            </button>
            {deleteUserMutation.isError ? (
                <p>Не удалось удалить аккаунт. Попробуйте ещё раз.</p>
            ) : null}
        </>
    )
}

function EditProfileForm({ user }: { user: User }) {
    const [name, setName] = useState(user.user_name || "");
    const [email, setEmail] = useState(user.user_email || "");
    const [password, setPassword] = useState("*******");
    const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
    const [avatarError, setAvatarError] = useState<string | null>(null);

    useEffect(() => {
        return () => {
            if (avatarPreview) {
                URL.revokeObjectURL(avatarPreview);
            }
        };
    }, [avatarPreview]);

    function handleAvatarChange(event: ChangeEvent<HTMLInputElement>) {
        const file = event.target.files?.[0];

        if (!file) {
            return;
        }

        if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
            setAvatarError("Выберите изображение JPEG, PNG или WebP.");
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            setAvatarError("Размер изображения не должен превышать 5 МБ.");
            return;
        }

        setAvatarPreview(URL.createObjectURL(file));
        setAvatarError(null);
    }

    const visibleAvatar = avatarPreview ?? user.user_photo;

    return (
        <form className="edit-profile-form" onSubmit={(event) => event.preventDefault()}>
            <div className="user-photo-container">
                {visibleAvatar ? (
                    <img
                        className="edit-user-avatar-image"
                        src={visibleAvatar}
                        alt={`Аватар ${user.user_name}`}
                    />
                ) : 
                (
                    <div className="user-photo-placeholder-conteiner">
                        <svg className="user-photo-placeholder" viewBox="0 0 19 23" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M19 23H16.625V20.8095C16.625 18.9948 15.0301 17.5238 13.0625 17.5238H5.9375C3.96999 17.5238 2.375 18.9948 2.375 20.8095V23H0V20.8095C0 17.7851 2.65831 15.3333 5.9375 15.3333H13.0625C16.3417 15.3333 19 17.7851 19 20.8095V23ZM9.5 13.1429C5.56497 13.1429 2.375 10.2007 2.375 6.57143C2.375 2.94213 5.56497 0 9.5 0C13.435 0 16.625 2.94213 16.625 6.57143C16.625 10.2007 13.435 13.1429 9.5 13.1429ZM9.5 10.9524C12.1233 10.9524 14.25 8.99096 14.25 6.57143C14.25 4.15189 12.1233 2.19048 9.5 2.19048C6.87665 2.19048 4.75 4.15189 4.75 6.57143C4.75 8.99096 6.87665 10.9524 9.5 10.9524Z" fill="currentColor"/>
                        </svg>
                    </div>
                )}

                <label className="change-avatar-button">
                    Изменить фото
                    <input
                        type="file"
                        accept="image/jpeg,image/png,image/webp"
                        hidden
                        onClick={(event) => {
                            event.currentTarget.value = "";
                        }}
                        onChange={handleAvatarChange}
                    />
                </label>

                {avatarError ? (
                    <p className="edit-user-avatar-error" role="alert">
                        {avatarError}
                    </p>
                ) : null}
            </div>

            <label className="edit-user-field">
                <span className="edit-user-label">Имя</span>
                <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                >
                </input>
            </label>
            
            <label className="edit-user-field">
                <span className="edit-user-label">Email</span>
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                >
                </input>
            </label>
            
            <label className="edit-user-field">
                <span className="edit-user-label">Пароль</span>
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled
                >
                </input>
            </label>
            
            <button
                className="save-button"
                type="submit"
            >
                Сохранить
            </button>
        </form>
    )
}
