import { 
    createRootRoute, 
    createRoute, 
    createRouter, 
    Outlet,
} from "@tanstack/react-router";

import { appRoutes } from "@/shared/constants/routes";

import { LoginPage } from "@/pages/auth/login-page";
import { HomePage } from "@/pages/home/home-page";
import { UserProfile } from "@/pages/profile/profile-page";
import { MapPage } from "@/pages/map/map-page";
import { ChatPage } from "@/pages/chat/chat-page";
import { CalendarPage } from "@/pages/calendar/calendar-page";
import { SignupPage } from "@/pages/auth/signup-page";

import { ensureAuth, redirectIfAuthenticated } from "./guards";

import { FullAppShell } from "@/widgets/app-shell/full-app-shell";
import { MainOnlyShell } from "@/widgets/app-shell/main-only-shell";

import { NotFoundPage } from "@/pages/not-found/not-found-page";

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

const signUpRoute = createRoute ({
    getParentRoute: () => rootRoute,
    path: appRoutes.signup,
    component: SignupPage,
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

const profileRoute = createRoute ({
    getParentRoute: () => fullAppLayoutRoute,
    path: appRoutes.userProfile,
    component: UserProfile,
});

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

const chatRoute = createRoute ({
    getParentRoute: () => mainOnlyLayoutRoute,
    path: appRoutes.chat,
    component: ChatPage,
});

const routeTree = rootRoute.addChildren([
    loginRoute,
    signUpRoute,
    
    protectedRoute.addChildren([
        fullAppLayoutRoute.addChildren([
            homeRoute,
            profileRoute,
            calendarRoute,
        ]),

        mainOnlyLayoutRoute.addChildren([
            mapRoute,
            chatRoute,
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