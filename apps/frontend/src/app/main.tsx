import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { Providers } from "@/app/providers";

import "@/app/styles/globals.css"

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <Providers />
    </StrictMode>
);

console.log('Vite env:', import.meta.env);
console.log(
  'Yandex key:',
  import.meta.env.VITE_YANDEX_MAPS_API_KEY
);