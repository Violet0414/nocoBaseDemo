"use client";

import { Header } from "@/components/app-shell/header";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { cn } from "@/lib/utils";
import type { PropsWithChildren } from "react";
import { useLocation } from "react-router";
import { PageErrorBoundary } from "./page-error-boundary";
import { Sidebar } from "./sidebar";

/**
 * 嵌入模式：URL 带 ?embed=1 时只渲染页面本体（无侧栏/顶栏/内边距）。
 * 用于 admin 门户 iframe 入口页（排课管理/课表查询/排座管理，见 docs/features/s9-portal-entry.md）。
 */
function isEmbedMode(search: string) {
  return new URLSearchParams(search).get("embed") === "1";
}

export function Layout({ children }: PropsWithChildren) {
  const location = useLocation();
  if (isEmbedMode(location.search)) {
    // 不锁 h-svh/overflow：内容自然生长，高度由外层入口页 jsBlock 同步（ResizeObserver），
    // 长页面（周课表+冲突卡）撑开 iframe 后由 admin 外层滚动条滚动
    return (
      <main className="relative flex w-full flex-col">
        <PageErrorBoundary>{children}</PageErrorBoundary>
      </main>
    );
  }
  return (
    <SidebarProvider>
      <Sidebar />
      <SidebarInset className="bg-muted/25">
        <Header />
        <main
          className={cn(
            "@container/main",
            "mx-auto",
            "max-w-[1600px]",
            "relative",
            "w-full",
            "flex",
            "flex-col",
            "flex-1",
            "px-4",
            "py-5",
            "md:p-6",
            "lg:px-8",
            "lg:py-7"
          )}
        >
          <PageErrorBoundary>{children}</PageErrorBoundary>
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}

Layout.displayName = "Layout";
