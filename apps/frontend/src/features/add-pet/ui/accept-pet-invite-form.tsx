import { FormEvent, useState } from "react";
import { useAcceptInvite } from "@/features/manage-share/model/use-accept-invite";

type AcceptInviteFormProps = {
    onAccepted: () => void;
    onCancel: () => void;
};

export function AcceptInviteForm({ onAccepted, onCancel }: AcceptInviteFormProps) {
    const acceptInvite = useAcceptInvite();
    const [inviteCode, setInviteCode] = useState("");

    function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();

        acceptInvite.mutate(inviteCode.trim(), {
            onSuccess: () => {
                setInviteCode("");
                onAccepted();
            },
        });
    }

    return (
        <form className="create-pet-form" onSubmit={handleSubmit}>
            <label className="create-pet-field">
                <span>Код доступа</span>
                <input
                    value={inviteCode}
                    onChange={(event) => setInviteCode(event.target.value)}
                    minLength={6}
                    maxLength={32}
                    placeholder="Введите код шеринга"
                    required
                />
            </label>

            {acceptInvite.isError ? (
                <p className="create-pet-error">
                    Не удалось добавить питомца по коду. Проверьте код и попробуйте ещё раз.
                </p>
            ) : null}

            <div className="create-pet-actions">
                <button type="button" onClick={onCancel}>
                    Отмена
                </button>
                <button type="submit" disabled={acceptInvite.isPending}>
                    {acceptInvite.isPending ? "Добавляем..." : "Добавить"}
                </button>
            </div>
        </form>
    );
}