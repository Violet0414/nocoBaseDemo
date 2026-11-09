import { Outlet, Navigate } from "react-router";
import { CalendarDays, LayoutGrid, Armchair, Clock } from "lucide-react";

import { defineAppRoutes } from "@nocobase/portal-sdk/routing";

// The application is the real 党校课表/排座 product; Registry demo routes stay off.
export const registryRoutesEnabled = false;

export const appRoutes = defineAppRoutes([
  {
    name: "scheduling",
    path: "/schedule",
    element: <Outlet />,
    resource: {
      meta: {
        label: "教学排课",
        group: true,
        icon: <CalendarDays />,
        priority: 1,
      },
    },
    children: [
      {
        name: "scheduling.index",
        index: true,
        element: <Navigate to="/schedule/week" replace />,
      },
      {
        name: "schedule-week",
        path: "week",
        lazy: () => import("@/features/scheduling/schedule-week"),
        resource: {
          meta: {
            label: "周课表",
            icon: <Clock />,
            singularLabel: "周课表",
            priority: 1,
          },
        },
      },
      {
        name: "schedule-board",
        path: "board",
        lazy: () => import("@/features/scheduling/schedule-board"),
        resource: {
          meta: {
            label: "排课画布",
            icon: <LayoutGrid />,
            singularLabel: "排课画布",
            priority: 2,
          },
        },
      },
      {
        name: "seat-map",
        path: "seats",
        lazy: () => import("@/features/scheduling/seat-map"),
        resource: {
          meta: {
            label: "座位表",
            icon: <Armchair />,
            singularLabel: "座位表",
            priority: 3,
          },
        },
      },
    ],
  },
]);
