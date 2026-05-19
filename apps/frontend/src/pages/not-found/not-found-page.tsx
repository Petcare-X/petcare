import { Link } from "@tanstack/react-router";

import { appRoutes } from "@/shared/constants/routes";

import "./not-found.css";

export function NotFoundPage() {
    return (
        <main className="not-found-page">
            <h1 className="not-found-code">404</h1>
            <p className="not-found-title">Похоже, кто-то съел эту страницу...</p>
            <p className="not-found-subtitle">К сожалению, мы не смогли ее найти, но вы можете перейти на главный экран.</p>
            
            <Link className="not-found-back-btn" to={appRoutes.home}>Вернуться на главную</Link>
        </main>
    );
}