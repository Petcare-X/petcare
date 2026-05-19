import { 
    createRootRoute, 
    createRoute, 
    createRouter, 
    Outlet,
} from "@tanstack/react-router";

import { appRoutes } from "@/shared/constants/routes";

import { LoginPage } from "@/pages/auth/login-page";
import { SignupPage } from "@/pages/auth/signup-page";

import { HomePage } from "@/pages/home/home-page";
import { UserProfile } from "@/pages/profile/profile-page";
import { EditProfilePage } from "@/pages/profile/edit-profile";
import { MapPage } from "@/pages/map/map-page";
import { CalendarPage } from "@/pages/calendar/calendar-page";
import { PetDetailsPage } from "@/pages/pets/pet-details-page";

import { ChatPetSelectPage } from "@/pages/chat/select-pet/chat-pet-select-page";
import { ChatHistoryPage } from "@/pages/chat/history/chat-history-page";
import { ChatPage } from "@/pages/chat/page/chat-page";

import { ensureAuth, redirectIfAuthenticated } from "./guards";

import { FullAppShell } from "@/widgets/app-shell/full-app-shell";
import { MainOnlyShell } from "@/widgets/app-shell/main-only-shell";
import { NavbarOnlyShell } from "@/widgets/app-shell/navbar-only-shell";

import { NotFoundPage } from "@/pages/not-found/not-found-page";

import { EditPetPage } from "@/pages/pets/edit-pet-page";
import { PetDocumentsPage } from "@/pages/documents/pet-documents-page";


const rootRoute = createRootRoute ({
    component: () => <Outlet />,
    notFoundComponent: NotFoundPage,
});

const protectedRoute = createRoute ({
    getParentRoute: () => rootRoute,
    id: "protected",
    beforeLoad: ensureAuth,
    component: () => <Outlet />,
    notFoundComponent: NotFoundPage,
});

const fullAppLayoutRoute = createRoute({
    getParentRoute: () => protectedRoute,
    id: "app-layout",
    component: FullAppShell,
    notFoundComponent: NotFoundPage,
});

const mainOnlyLayoutRoute = createRoute({
    getParentRoute: () => protectedRoute,
    id: "main-only-layout",
    component: MainOnlyShell,
    notFoundComponent: NotFoundPage,
});

const navbarOnlyLayoutRoute = createRoute({
    getParentRoute: () => protectedRoute,
    id: "navbar-only-layout",
    component: NavbarOnlyShell,
    notFoundComponent: NotFoundPage,
});

const signUpRoute = createRoute ({
    getParentRoute: () => rootRoute,
    path: appRoutes.signup,
    component: SignupPage,
    beforeLoad: redirectIfAuthenticated,
});

const authRoute = createRoute ({
    getParentRoute: () => rootRoute,
    path: appRoutes.auth,
    component: LoginPage,
    beforeLoad: redirectIfAuthenticated,
});

const loginRoute = createRoute ({
    getParentRoute: () => rootRoute,
    path: appRoutes.login,
    component: LoginPage,
    beforeLoad: redirectIfAuthenticated,
});

const homeRoute = createRoute ({
    getParentRoute: () => fullAppLayoutRoute,
    path: appRoutes.home,
    component: HomePage,
});

const petDetailsRoute = createRoute ({
    getParentRoute: () => mainOnlyLayoutRoute,
    path: appRoutes.petProfile,
    component: PetDetailsPage,
});

const editPetRoute = createRoute ({
    getParentRoute: () => mainOnlyLayoutRoute,
    path: appRoutes.editPetProfile,
    component: EditPetPage,
});

const profileRoute = createRoute ({
    getParentRoute: () => fullAppLayoutRoute,
    path: appRoutes.userProfile,
    component: UserProfile,
});

const editProfileRoute = createRoute({
    getParentRoute: () => fullAppLayoutRoute,
    path: appRoutes.editProfile,
    component: EditProfilePage,
})

const calendarRoute = createRoute ({
    getParentRoute: () => mainOnlyLayoutRoute,
    path: appRoutes.calendar,
    component: CalendarPage,
});

export const mapRoute = createRoute ({
    getParentRoute: () => mainOnlyLayoutRoute,
    path: appRoutes.map,
    component: MapPage,
    validateSearch: (search: Record<string, unknown>) => ({
        filter:
            search.filter === "clinic"  ||
            search.filter === "place" ||
            search.filter === "salon"
                ? search.filter : undefined
    }),
});

const chatPetSelectRoute = createRoute ({
    getParentRoute: () => navbarOnlyLayoutRoute,
    path: appRoutes.chatSelectPet,
    component: ChatPetSelectPage,
});

const chatHistoryRoute = createRoute ({
    getParentRoute: () => navbarOnlyLayoutRoute,
    path: appRoutes.chatHistory,
    component: ChatHistoryPage,
});

const chatRoute = createRoute ({
    getParentRoute: () => mainOnlyLayoutRoute,
    path: appRoutes.chat,
    component: ChatPage,
});

const documentsRoute = createRoute({
    getParentRoute: () => mainOnlyLayoutRoute,
    path: appRoutes.documents,
    component: PetDocumentsPage,
})

const routeTree = rootRoute.addChildren([
    authRoute,
    loginRoute,
    signUpRoute,
    
    protectedRoute.addChildren([
        fullAppLayoutRoute.addChildren([
            homeRoute,
            profileRoute,
            editProfileRoute,
        ]),

        mainOnlyLayoutRoute.addChildren([
            petDetailsRoute,
            mapRoute,
            chatRoute,
            editPetRoute,
            calendarRoute,
            documentsRoute,
        ]),

        navbarOnlyLayoutRoute.addChildren([
            chatPetSelectRoute,
            chatHistoryRoute,
        ]),
    ]),
]);

export const router =createRouter({
    routeTree
});

declare module "@tanstack/react-router" {
    interface Register {
        router: typeof router;
    }
};
