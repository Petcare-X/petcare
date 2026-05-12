import { Outlet } from "@tanstack/react-router";
import { Header } from "@/widgets/app-shell/page-header";
import { Navbar } from "@/widgets/app-shell/page-navbar";

import "./app-shell.css";

export function FullAppShell() {
    return (
        <div>
            <Header />

            <main className="main-content-with-shell page-transition">
                <Outlet />
            </main>
            
            <Navbar />
        </div>
    )
}