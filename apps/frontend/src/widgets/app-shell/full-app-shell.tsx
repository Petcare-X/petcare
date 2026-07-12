import { Outlet } from "@tanstack/react-router";
import { Header } from "@/widgets/header/page-header";
import { Navbar } from "@/widgets/navbar/page-navbar";

import "./app-shell.css";

export function FullAppShell() {
    return (
        <>
            <Header />

            <main className="main-content-with-shell page-transition">
                <Outlet />
            </main>
            
            <Navbar />
        </>
    )
}