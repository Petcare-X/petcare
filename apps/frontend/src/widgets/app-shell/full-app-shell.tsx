import { Outlet } from "@tanstack/react-router";
import { Header } from "@/widgets/app-shell/page-header";
import { Navbar } from "@/widgets/app-shell/page-navbar";

import "./app-shell.css";

export function FullAppShell() {
    return (
        <div className="app-shell">
            <Header />

            <main className="main-content page-transition">
                <Outlet />
            </main>
            
            <Navbar />
        </div>
    )
}