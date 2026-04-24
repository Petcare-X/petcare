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
import { requireAuth } from "./guards";

const rootRoute = createRootRoute ({
    component: () => <Outlet />
});

const protectedRoute = createRoute ({
    getParentRoute: () => rootRoute,
    id: "protected",
    beforeLoad: requireAuth,
    component: () => <Outlet />,
});

const loginRoute = createRoute ({
    getParentRoute: () => rootRoute,
    path: "/auth/login",
    component: LoginPage,
});

const homeRoute = createRoute ({
    getParentRoute: () => protectedRoute,
    path: appRoutes.home,
    component: HomePage,
});

const profileRoute = createRoute ({
    getParentRoute: () => protectedRoute,
    path: appRoutes.userProfile,
    component: UserProfile,
})

const routeTree = rootRoute.addChildren([
    loginRoute,
    
    protectedRoute.addChildren([ homeRoute,
    profileRoute,
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