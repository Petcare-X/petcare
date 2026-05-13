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

import { ChatPetSelectPage } from "@/pages/chat/chat-pet-select-page";
import { ChatHistoryPage } from "@/pages/chat/chat-history-page";
import { ChatPage } from "@/pages/chat/chat-page";

import { ensureAuth, redirectIfAuthenticated } from "./guards";

import { FullAppShell } from "@/widgets/app-shell/full-app-shell";
import { MainOnlyShell } from "@/widgets/app-shell/main-only-shell";
import { NavbarOnlyShell } from "@/widgets/app-shell/navbar-only-shell";

import { NotFoundPage } from "@/pages/not-found/not-found-page";

import { EditPetPage } from "@/pages/pets/edit-pet-page";


const rootRoute = createRootRoute ({
    component: () => <Outlet />,
    notFoundComponent: NotFoundPage,
});

const protectedRoute = createRoute ({
    getParentRoute: () => rootRoute,
    id: "protected",
    beforeLoad: ensureAuth,
    component: () => <Outlet />,
});

const fullAppLayoutRoute = createRoute({
    getParentRoute: () => protectedRoute,
    id: "app-layout",
    component: FullAppShell,
});

const mainOnlyLayoutRoute = createRoute({
    getParentRoute: () => protectedRoute,
    id: "main-only-layout",
    component: MainOnlyShell,
});

const navbarOnlyLayoutRoute = createRoute({
    getParentRoute: () => protectedRoute,
    id: "navbar-only-layout",
    component: NavbarOnlyShell,
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
    getParentRoute: () => fullAppLayoutRoute,
    path: appRoutes.calendar,
    component: CalendarPage,
});

const mapRoute = createRoute ({
    getParentRoute: () => mainOnlyLayoutRoute,
    path: appRoutes.map,
    component: MapPage,
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

const routeTree = rootRoute.addChildren([
    authRoute,
    loginRoute,
    signUpRoute,
    
    protectedRoute.addChildren([
        fullAppLayoutRoute.addChildren([
            homeRoute,
            profileRoute,
            calendarRoute,
            editProfileRoute,
        ]),

        mainOnlyLayoutRoute.addChildren([
            petDetailsRoute,
            mapRoute,
            chatRoute,
            editPetRoute,
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
