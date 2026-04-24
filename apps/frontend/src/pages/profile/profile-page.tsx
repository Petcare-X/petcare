import { useLogout } from "@/features/auth/model/use-logout";

import "./profile-page.css"

export function UserProfile () {
    const logout = useLogout();

    return (
        <div className="profile-page">
            <div>Профиль пользоавтеля</div>
            <button 
                className="logout-button"
                type="button" 
                onClick={() => logout.mutate()}
                disabled={logout.isPending}
            >
                {logout.isPending ? "Выходим..." : "Выход"}
            </button>
        </div>
    );
}