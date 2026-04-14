import { 
    createRootRoute, 
    createRoute, 
    createRouter, 
    Outlet,
} from "@tanstack/react-router";

import { appRoutes } from "@/shared/constants/routes";

import { HomePage } from "@/pages/home/home-page";
import { UserProfile } from "@/pages/profile/profile-page";

const rootRoute = createRootRoute ({
    component: () => <Outlet />
});

const homeRoute = createRoute ({
    getParentRoute: () => rootRoute,
    path: appRoutes.home,
    component: HomePage,
});

const profileRoute = createRoute ({
    getParentRoute: () => rootRoute,
    path: appRoutes.userProfile,
    component: UserProfile,
})

const routeTree = rootRoute.addChildren([
    homeRoute,
    profileRoute,
]);

export const router =createRouter({
    routeTree
});

declare module "@tanstack/react-router" {
    interface Register {
        router: typeof router;
    }
};