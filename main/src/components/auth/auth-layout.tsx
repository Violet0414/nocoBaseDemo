import type { PropsWithChildren, ReactNode } from "react";
import { Blocks, BookOpen, ShieldCheck } from "lucide-react";

import { Brand } from "@/components/app-shell/brand";

type AuthLayoutProps = PropsWithChildren<{
  title: string;
  description: string;
  footer?: ReactNode;
}>;

export function AuthLayout({
  title,
  description,
  footer,
  children,
}: AuthLayoutProps) {
  return (
    <div className="grid min-h-svh md:grid-cols-[minmax(420px,44%)_1fr]">
      <main className="grid place-items-center bg-card px-6 py-10 sm:px-12">
        <div className="w-full max-w-sm">
          <Brand className="mb-14" logoClassName="h-10" />
          <h1 className="text-3xl font-semibold tracking-[-0.035em]">
            {title}
          </h1>
          <p className="mb-8 mt-2 text-sm text-muted-foreground">
            {description}
          </p>
          {children}
          {footer && <div className="mt-8 text-sm">{footer}</div>}
        </div>
      </main>

      <section className="relative hidden overflow-hidden bg-blue-50 p-12 text-blue-950 md:grid md:place-items-center">
        <div className="absolute inset-0 opacity-[0.08] [background-image:linear-gradient(currentColor_1px,transparent_1px),linear-gradient(90deg,currentColor_1px,transparent_1px)] [background-size:48px_48px]" />
        <div className="relative w-full max-w-xl">
          <div className="text-xs font-semibold uppercase tracking-[0.14em] text-blue-800/80">
            党校智慧管理平台
          </div>
          <h2 className="mt-3 max-w-lg text-5xl font-semibold leading-[1.08] tracking-[-0.04em]">
            教学、学员、教务一体化管理
          </h2>
          <p className="mt-5 max-w-lg text-base leading-7 text-blue-900/70">
            面向校领导、教职工与学员的综合管理平台：班次排课、审批考勤、评估统计，一站式完成。
          </p>

          <div className="mt-10 max-w-md rounded-xl border border-blue-200/70 bg-white p-5 text-neutral-900 shadow-2xl shadow-blue-900/10">
            <div className="flex items-center gap-3">
              <div className="grid size-10 place-items-center rounded-lg bg-neutral-100">
                <BookOpen className="size-4" />
              </div>
              <div>
                <div className="font-semibold">教学教务</div>
                <div className="text-sm text-neutral-500">
                  班次管理、教学计划、智能排课与教材管理。
                </div>
              </div>
            </div>
            <div className="my-5 h-px bg-neutral-200" />
            <div className="flex items-center gap-3">
              <div className="grid size-10 place-items-center rounded-lg bg-neutral-100">
                <ShieldCheck className="size-4" />
              </div>
              <div>
                <div className="font-semibold">学员服务</div>
                <div className="text-sm text-neutral-500">
                  报名审批、请假考勤、评估问卷与移动端。
                </div>
              </div>
            </div>
            <div className="mt-5 flex items-center gap-2 rounded-lg bg-blue-100/70 px-3 py-2 text-xs font-medium text-blue-900">
              <Blocks className="size-3.5" />
              统一数据、权限与审批流程
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
