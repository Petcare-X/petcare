import { useDeleteAccount } from "@/features/delete-user/model/use-delete-user";

import "./profile-page.css"

export function EditProfilePage() {
    const deleteUserMutation = useDeleteAccount();

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
        <div
            style={{
                display: "flex",
                justifyContent: "center",
            }}
        >
            <button
                className="logout-button"
                type="button"
                onClick={() => void handleDeleteAccount()}
                disabled={deleteUserMutation.isPending}
            >
                {deleteUserMutation.isPending ? "Удаляем..." : "Удалить аккаунт"}
            </button>
            {deleteUserMutation.isError ? (
                <p>Не удалось удалить аккаунт. Попробуйте ещё раз.</p>
            ) : null}
        </div>
    )
}