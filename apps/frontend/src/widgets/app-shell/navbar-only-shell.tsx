import { Outlet } from "@tanstack/react-router"

import { Navbar } from "./page-navbar"

export function NavbarOnlyShell() {
    return (
        <div>
            <main className="main-content-with-shell page-transition">
                <Outlet />
            </main>

            <Navbar />
        </div>
    )
}