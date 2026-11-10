import type { RenderAuthenticator } from "@nocobase/portal-sdk/auth";

import { AuthLayout } from "@/components/auth/auth-layout";
import { DynamicSignIn } from "@/components/auth/dynamic-sign-in";

type DefaultSignInPageProps = {
  renderAuthenticator?: RenderAuthenticator;
};

export function DefaultSignInPage({
  renderAuthenticator,
}: DefaultSignInPageProps) {
  return (
    <AuthLayout
      title="欢迎回来"
      description="选择登录方式，登录党校智慧管理平台。"
    >
      <DynamicSignIn renderAuthenticator={renderAuthenticator} />
    </AuthLayout>
  );
}
