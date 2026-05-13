import { Link } from "@tanstack/react-router";

import { appRoutes } from "@/shared/constants/routes";

import "./not-found.css";

export function NotFoundPage() {
    return (
        <main className="not-found-page">
            <div className="not-found-page-content">
                <h1 className="not-found-code">404</h1>
                <p className="not-found-message">Страница не найдена</p>

                <Link className="to-main-button" to={appRoutes.home}>Вернуться на главную</Link>
            </div>
        </main>
    );
}