import { useLogout } from "@/features/auth/model/use-logout";
import { useUserQueries } from "@/entities/user/model/user.queries";

import "./profile-page.css"
import { Link } from "@tanstack/react-router";
import { appRoutes } from "@/shared/constants/routes";

export function UserProfile () {
    const logout = useLogout();

    const user = useUserQueries().data;

    return (
        <>
            <div className="user-info">
                {user?.user_photo ? (
                    <img src={user.user_photo} />
                ) : 
                (
                    <div className="user-photo-placeholder-conteiner">
                        <svg className="user-photo-placeholder" viewBox="0 0 19 23" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M19 23H16.625V20.8095C16.625 18.9948 15.0301 17.5238 13.0625 17.5238H5.9375C3.96999 17.5238 2.375 18.9948 2.375 20.8095V23H0V20.8095C0 17.7851 2.65831 15.3333 5.9375 15.3333H13.0625C16.3417 15.3333 19 17.7851 19 20.8095V23ZM9.5 13.1429C5.56497 13.1429 2.375 10.2007 2.375 6.57143C2.375 2.94213 5.56497 0 9.5 0C13.435 0 16.625 2.94213 16.625 6.57143C16.625 10.2007 13.435 13.1429 9.5 13.1429ZM9.5 10.9524C12.1233 10.9524 14.25 8.99096 14.25 6.57143C14.25 4.15189 12.1233 2.19048 9.5 2.19048C6.87665 2.19048 4.75 4.15189 4.75 6.57143C4.75 8.99096 6.87665 10.9524 9.5 10.9524Z" fill="currentColor"/>
                        </svg>
                    </div>
                )}
                <h1 className="user-name">{user?.user_name}</h1>
            </div>

            <div className="profile-links-list">
                <Link to={appRoutes.editProfile} className="profile-link-item">
                    <div className="profile-link-icon">
                        <svg width="19" height="23" viewBox="0 0 19 23" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M19 23H16.625V20.8095C16.625 18.9948 15.0301 17.5238 13.0625 17.5238H5.9375C3.96999 17.5238 2.375 18.9948 2.375 20.8095V23H0V20.8095C0 17.7851 2.65831 15.3333 5.9375 15.3333H13.0625C16.3417 15.3333 19 17.7851 19 20.8095V23ZM9.5 13.1429C5.56497 13.1429 2.375 10.2007 2.375 6.57143C2.375 2.94213 5.56497 0 9.5 0C13.435 0 16.625 2.94213 16.625 6.57143C16.625 10.2007 13.435 13.1429 9.5 13.1429ZM9.5 10.9524C12.1233 10.9524 14.25 8.99096 14.25 6.57143C14.25 4.15189 12.1233 2.19048 9.5 2.19048C6.87665 2.19048 4.75 4.15189 4.75 6.57143C4.75 8.99096 6.87665 10.9524 9.5 10.9524Z" fill="black"/>
                        </svg>
                    </div>
                    Аккаунт
                    <div className="profile-arrow-icon">
                        <svg width="12" height="19" viewBox="0 0 12 19" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M7.21843 9.2808L0 2.06239L2.0624 0L11.3432 9.2808L2.0624 18.5615L0 16.4991L7.21843 9.2808Z" fill="#B2B2B2"/>
                        </svg>
                    </div>
                </Link>
                <Link to={appRoutes.userProfile} className="profile-link-item">
                    <div className="profile-link-icon">
                        <svg width="20" height="23" viewBox="0 0 20 23" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M9.89583 0L19.7917 5.72917V17.1875L9.89583 22.9167L0 17.1875V5.72917L9.89583 0ZM9.89583 2.40729L2.08333 6.93032V15.9864L9.89583 20.5094L17.7083 15.9864V6.93032L9.89583 2.40729ZM9.89583 15.625C7.59465 15.625 5.72917 13.7595 5.72917 11.4583C5.72917 9.15715 7.59465 7.29167 9.89583 7.29167C12.197 7.29167 14.0625 9.15715 14.0625 11.4583C14.0625 13.7595 12.197 15.625 9.89583 15.625ZM9.89583 13.5417C11.0465 13.5417 11.9792 12.609 11.9792 11.4583C11.9792 10.3077 11.0465 9.375 9.89583 9.375C8.74521 9.375 7.8125 10.3077 7.8125 11.4583C7.8125 12.609 8.74521 13.5417 9.89583 13.5417Z" fill="black"/>
                        </svg>
                    </div>
                    Настройки
                    <div className="profile-arrow-icon">
                        <svg width="12" height="19" viewBox="0 0 12 19" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M7.21843 9.2808L0 2.06239L2.0624 0L11.3432 9.2808L2.0624 18.5615L0 16.4991L7.21843 9.2808Z" fill="#B2B2B2"/>
                        </svg>
                    </div>
                </Link>
                <Link to={appRoutes.userProfile} className="profile-link-item">
                    <div className="profile-link-icon">
                        <svg width="21" height="20" viewBox="0 0 21 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M10.4177 1.59222C12.8646 -0.604166 16.6458 -0.531249 19.0027 1.83058C21.3597 4.19242 21.4406 7.95521 19.2485 10.4094L10.4166 19.2552L1.58477 10.4094C-0.607241 7.95521 -0.525304 4.18647 1.83058 1.83058C4.18913 -0.527968 7.96374 -0.607426 10.4177 1.59222ZM17.5281 3.30219C15.9666 1.73744 13.4454 1.67397 11.8094 3.14257L10.4186 4.39088L9.02718 3.14355C7.38643 1.67289 4.86985 1.73758 3.30372 3.30372C1.7519 4.85553 1.674 7.34094 3.10409 8.9825L10.4166 16.3066L17.7293 8.9825C19.1599 7.34031 19.0823 4.85964 17.5281 3.30219Z" fill="black"/>
                        </svg>
                    </div>
                    Помощь
                    <div className="profile-arrow-icon">
                        <svg width="12" height="19" viewBox="0 0 12 19" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M7.21843 9.2808L0 2.06239L2.0624 0L11.3432 9.2808L2.0624 18.5615L0 16.4991L7.21843 9.2808Z" fill="#B2B2B2"/>
                        </svg>
                    </div>
                </Link>
            </div>

            <button 
                className="logout-button"
                type="button" 
                onClick={() => logout.mutate()}
                disabled={logout.isPending}
            >
                {logout.isPending ? "Выходим..." : "Выход"}
            </button>
        </>
    );
}