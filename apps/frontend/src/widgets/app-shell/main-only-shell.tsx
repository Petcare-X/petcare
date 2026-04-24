import { Outlet } from "@tanstack/react-router";

import "./app-shell.css";

export function MainOnlyShell() {
    return (
        <main className="main-content page-transition">
            <Outlet />
        </main>
    )
}