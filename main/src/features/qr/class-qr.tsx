import { useCallback, useEffect, useMemo, useState } from "react";
import QRCode from "qrcode";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { PageErrorBoundary } from "@/components/app-shell/page-error-boundary";
import { LoadingState } from "@/components/app-shell/loading-state";

import { CLASS_RESOURCE, listResource, type Klass } from "../scheduling/api";

// 学员移动端「扫码报名」页 pageSchemaUid
const REGISTRATION_PAGE_PATH = "/mobile/3cfhfajaa4x";

function useQueryToken(): string {
  return useMemo(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get("token") ?? "";
  }, []);
}

function ClassQrInner() {
  const tokenFromQuery = useQueryToken();
  const [classes, setClasses] = useState<Klass[]>([]);
  const [token, setToken] = useState(tokenFromQuery);
  const [klass, setKlass] = useState<Klass | null>(null);
  const [dataUrl, setDataUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (tokenFromQuery) return;
    let cancelled = false;
    listResource<Klass>(CLASS_RESOURCE, { sort: "-id" })
      .then((rows) => !cancelled && setClasses(rows))
      .catch(() => !cancelled && setError("班次列表加载失败"));
    return () => {
      cancelled = true;
    };
  }, [tokenFromQuery]);

  const loadKlass = useCallback(async (tk: string) => {
    if (!tk) return;
    setLoading(true);
    setError(null);
    try {
      const rows = await listResource<Klass>(CLASS_RESOURCE, {
        filter: { qr_token: tk },
        pageSize: 1,
      });
      setKlass(rows[0] ?? null);
      if (!rows[0]) setError("未找到对应班次");
    } catch {
      setError("班次信息加载失败");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (tokenFromQuery) return;
    const selected = classes.find((c) => String(c.id) === token);
    setKlass(selected ?? null);
  }, [token, classes, tokenFromQuery]);

  useEffect(() => {
    void loadKlass(tokenFromQuery);
  }, [tokenFromQuery, loadKlass]);

  useEffect(() => {
    if (!klass?.id) {
      setDataUrl("");
      return;
    }
    const url = `${window.location.origin}${REGISTRATION_PAGE_PATH}?class=${klass.id}`;
    QRCode.toDataURL(url, {
      width: 320,
      margin: 2,
      errorCorrectionLevel: "M",
    })
      .then(setDataUrl)
      .catch(() => setError("二维码生成失败"));
  }, [klass]);

  const download = () => {
    if (!dataUrl) return;
    const a = document.createElement("a");
    a.href = dataUrl;
    a.download = `报名二维码-${klass?.name || token}.png`;
    a.click();
  };

  return (
    <div className="mx-auto flex max-w-md flex-col gap-4 p-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">班次报名二维码</CardTitle>
          <CardDescription>
            学员扫码进入移动端报名页，自动带上对应班次
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center gap-4">
          {!tokenFromQuery && (
            <Select
              value={token}
              onValueChange={(v) => v && setToken(v)}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="选择班次" />
              </SelectTrigger>
              <SelectContent>
                {classes.map((c) => (
                  <SelectItem key={c.id} value={String(c.id)}>
                    {c.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          {loading && <LoadingState />}
          {error && <p className="text-sm text-destructive">{error}</p>}
          {!token && !loading && !tokenFromQuery && (
            <p className="text-sm text-muted-foreground">
              请选择班次生成报名二维码，或从班次管理页点击「报名二维码」进入
            </p>
          )}
          {klass && dataUrl && (
            <>
              <p className="text-lg font-medium">{klass.name}</p>
              <img
                src={dataUrl}
                alt={`报名二维码 ${klass.name}`}
                className="h-80 w-80 rounded-md border"
              />
              <p className="break-all text-center text-xs text-muted-foreground">
                报名链接：{window.location.origin}
                {REGISTRATION_PAGE_PATH}?class={klass.id}
              </p>
              <Button onClick={download}>下载二维码图片</Button>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function ClassQrPage() {
  return (
    <PageErrorBoundary>
      <ClassQrInner />
    </PageErrorBoundary>
  );
}
