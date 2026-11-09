import { useCallback, useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { PageErrorBoundary } from "@/components/app-shell/page-error-boundary";
import { LoadingState } from "@/components/app-shell/loading-state";

import {
  CLASS_RESOURCE,
  DAY_LABELS,
  SCHEDULE_RESOURCE,
  TIME_SLOTS,
  type CourseSchedule,
  type Klass,
  dayFromTime,
  detectConflicts,
  listResource,
  slotFromTime,
} from "./api";

const KIND_LABELS: Record<string, string> = {
  lecture: "专题授课",
  activity: "教学活动",
  elective: "选修课",
  exam: "考核",
};

function scheduleCellText(item: CourseSchedule) {
  const topic =
    typeof item.topic === "object" && item.topic?.name
      ? item.topic.name
      : (item.topic_name ?? "");
  const teacher =
    typeof item.teacher === "object" && item.teacher?.name
      ? ` · ${item.teacher.name}`
      : "";
  const place = item.place ? ` · ${item.place}` : "";
  return { topic, detail: `${teacher}${place}` };
}

function WeekScheduleInner() {
  const [classes, setClasses] = useState<Klass[]>([]);
  const [classId, setClassId] = useState<string>("");
  const [week, setWeek] = useState("1");
  const [schedules, setSchedules] = useState<CourseSchedule[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    listResource<Klass>(CLASS_RESOURCE, { sort: "-id" })
      .then((rows) => {
        if (cancelled) return;
        setClasses(rows);
        if (rows[0]) setClassId(String(rows[0].id));
      })
      .catch(() => !cancelled && setError("班次列表加载失败"));
    return () => {
      cancelled = true;
    };
  }, []);

  const load = useCallback(async () => {
    if (!classId) return;
    setLoading(true);
    setError(null);
    try {
      const rows = await listResource<CourseSchedule>(SCHEDULE_RESOURCE, {
        filter: { class_id: Number(classId), week_no: Number(week) },
        appends: ["topic", "teacher"],
      });
      setSchedules(rows);
    } catch {
      setError("课表加载失败");
    } finally {
      setLoading(false);
    }
  }, [classId, week]);

  useEffect(() => {
    void load();
  }, [load]);

  const cellMap = useMemo(() => {
    const map = new Map<string, CourseSchedule[]>();
    for (const item of schedules) {
      const day = item.day_of_week ?? dayFromTime(item.start_time);
      const slot = slotFromTime(item.start_time, item.end_time);
      const key = `${day}-${slot}`;
      const list = map.get(key);
      if (list) list.push(item);
      else map.set(key, [item]);
    }
    return map;
  }, [schedules]);

  const conflicts = useMemo(() => detectConflicts(schedules), [schedules]);
  const conflictKeys = useMemo(
    () => new Set(conflicts.map((c) => `${c.day}-${c.slot}`)),
    [conflicts],
  );

  const totalHours = schedules.length;

  return (
    <div className="flex flex-col gap-4 p-4">
      <div className="flex flex-wrap items-center gap-3">
        <Select value={classId} onValueChange={(v) => setClassId(v ?? "")}>
          <SelectTrigger className="w-[220px]">
            <SelectValue placeholder="选择班次" />
          </SelectTrigger>
          <SelectContent>
            {classes.map((k) => (
              <SelectItem key={k.id} value={String(k.id)}>
                {k.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={week} onValueChange={(v) => setWeek(v ?? "")}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="选择周次" />
          </SelectTrigger>
          <SelectContent>
            {[1, 2, 3, 4, 5, 6, 7, 8].map((w) => (
              <SelectItem key={w} value={String(w)}>
                第 {w} 周
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Badge variant="secondary">共 {totalHours} 节</Badge>
        {conflicts.length > 0 && (
          <Badge variant="destructive">{conflicts.length} 处冲突</Badge>
        )}
        <Button variant="outline" size="sm" onClick={() => void load()} disabled={loading}>
          刷新
        </Button>
      </div>

      {error && <p className="text-sm text-destructive">{error}</p>}
      {loading ? (
        <LoadingState />
      ) : (
        <div className="overflow-x-auto rounded-lg border">
          <Table className="min-w-[760px] table-fixed">
            <TableHeader>
              <TableRow>
                <TableHead className="w-[90px]">时段</TableHead>
                {DAY_LABELS.map((d) => (
                  <TableHead key={d} className="text-center">
                    {d}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {TIME_SLOTS.map((slot) => (
                <TableRow key={slot.key}>
                  <TableCell className="whitespace-nowrap text-xs text-muted-foreground">
                    <div className="font-medium text-foreground">{slot.label}</div>
                    <div>
                      {slot.start}–{slot.end}
                    </div>
                  </TableCell>
                  {DAY_LABELS.map((_, dayIdx) => {
                    const day = dayIdx + 1;
                    const key = `${day}-${slot.key}`;
                    const items = cellMap.get(key) ?? [];
                    const hasConflict = conflictKeys.has(key);
                    return (
                      <TableCell
                        key={key}
                        className={`h-[64px] align-top p-1 ${
                          hasConflict ? "bg-destructive/10" : ""
                        }`}
                      >
                        {items.map((item) => {
                          const { topic, detail } = scheduleCellText(item);
                          return (
                            <div
                              key={item.id}
                              className="mb-1 rounded-md border bg-muted/60 px-2 py-1 text-xs"
                              title={detail}
                            >
                              <div className="truncate font-medium">{topic}</div>
                              <div className="truncate text-muted-foreground">
                                {detail || KIND_LABELS[item.kind ?? ""] || ""}
                              </div>
                            </div>
                          );
                        })}
                        {items.length === 0 && (
                          <div className="text-center text-xs text-muted-foreground/50">—</div>
                        )}
                      </TableCell>
                    );
                  })}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">冲突提示</CardTitle>
          <CardDescription>同一教师或同一教室在同一时段被重复安排时给出提醒</CardDescription>
        </CardHeader>
        <CardContent>
          {conflicts.length === 0 ? (
            <p className="text-sm text-muted-foreground">本周无冲突。</p>
          ) : (
            <ul className="list-disc space-y-1 pl-5 text-sm">
              {conflicts.map((c) => (
                <li key={`${c.day}-${c.slot}`}>
                  {DAY_LABELS[c.day - 1]} {TIME_SLOTS[c.slot - 1]?.label}：{c.reason}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function WeekSchedulePage() {
  return (
    <PageErrorBoundary>
      <WeekScheduleInner />
    </PageErrorBoundary>
  );
}
