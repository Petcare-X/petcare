import { Outlet } from "@tanstack/react-router"

import { Navbar } from "./page-navbar"

export function NavbarOnlyShell() {
    return (
        <>
            <main className="main-content-with-shell page-transition">
                <Outlet />
            </main>

            <Navbar />
        </>
    )
}