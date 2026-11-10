import { NocoBaseErrorBoundary } from "@/extensions/nocobase-error-boundary";
import { useTranslate } from "@refinedev/core";
import type { PropsWithChildren } from "react";
import { useLocation, useNavigate } from "react-router";

export function PageErrorBoundary({ children }: PropsWithChildren) {
  const location = useLocation();
  const navigate = useNavigate();
  const translate = useTranslate();

  return (
    <NocoBaseErrorBoundary
      variant="page"
      resetKeys={[location.pathname, location.search, location.hash]}
      context={{
        route: location.pathname,
        templateName: __PORTAL_TEMPLATE_NAME__,
        templateVersion: __PORTAL_TEMPLATE_VERSION__,
      }}
      labels={{
        title: translate(
          "runtimeError.title",
          "页面出错了"
        ),
        description: translate(
          "runtimeError.description",
          "该页面无法正常显示，如需反馈问题可复制诊断信息。"
        ),
        details: translate(
          "runtimeError.details",
          "诊断信息"
        ),
        copyDetails: translate(
          "runtimeError.copyDetails",
          "复制诊断信息"
        ),
        copied: translate("runtimeError.copied", "已复制"),
        copyFailed: translate("runtimeError.copyFailed", "复制失败"),
        retry: translate("runtimeError.retry", "重试"),
        reload: translate("runtimeError.reload", "刷新页面"),
        backHome: translate("runtimeError.backHome", "返回首页"),
      }}
      onBackHome={() => navigate("/")}
    >
      {children}
    </NocoBaseErrorBoundary>
  );
}
