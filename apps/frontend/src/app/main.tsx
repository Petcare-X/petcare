import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { Providers } from "@/app/providers";
import HomePage from "@/pages/home/home-page";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <HomePage />
        <Providers />
    </StrictMode>
);