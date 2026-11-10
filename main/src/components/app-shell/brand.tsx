import { cn } from "@/lib/utils";

export const BRAND_NAME = "党校智慧管理平台";

type BrandLogoProps = {
  className?: string;
};

export function BrandLogo({ className }: BrandLogoProps) {
  return (
    <span
      className={cn(
        "inline-flex size-10 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-gradient-to-br from-red-600 to-red-900 text-xl font-bold text-white",
        className
      )}
      aria-hidden="true"
    >
      党
    </span>
  );
}

export function BrandWordmark({ className }: BrandLogoProps) {
  return (
    <span
      className={cn(
        "inline-flex h-8 shrink-0 items-center overflow-hidden text-xl font-bold tracking-tight text-foreground whitespace-nowrap",
        className
      )}
    >
      {BRAND_NAME}
    </span>
  );
}
type BrandProps = {
  className?: string;
  logoClassName?: string;
  showText?: boolean;
};

export function Brand({
  className,
  logoClassName,
  showText = true,
}: BrandProps) {
  return (
    <div className={cn("flex min-w-0 items-center gap-2", className)}>
      <BrandLogo className={logoClassName} />
      {showText ? <BrandWordmark /> : null}
    </div>
  );
}
