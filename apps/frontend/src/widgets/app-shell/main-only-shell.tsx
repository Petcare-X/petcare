import { Outlet } from "@tanstack/react-router";

import "./app-shell.css";

export function MainOnlyShell() {
    return (
        <Outlet />
    )
}