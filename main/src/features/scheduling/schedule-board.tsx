import { useCallback, useEffect, useMemo, useState, type DragEvent } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { PageErrorBoundary } from "@/components/app-shell/page-error-boundary";
import { LoadingState } from "@/components/app-shell/loading-state";

import {
  CHANGE_LOG_RESOURCE,
  CLASS_RESOURCE,
  DAY_LABELS,
  SCHEDULE_RESOURCE,
  TIME_SLOTS,
  TOPIC_RESOURCE,
  type CourseSchedule,
  type Klass,

  type Topic,
  createRecord,
  dayFromTime,
  detectConflicts,
  listResource,
  resolveId,
  slotFromTime,
  updateRecord,
} from "./api";

interface DragPayload {
  topicId?: number;
  scheduleId?: number;
}

function topicLabel(topic: Topic | number | null | undefined): string {
  return typeof topic === "object" && topic?.name ? topic.name : "";
}

function itemLabel(item: CourseSchedule) {
  const name = topicLabel(item.topic) || item.topic_name || "未命名课程";
  const teacher =
    typeof item.teacher === "object" && item.teacher?.name ? ` · ${item.teacher.name}` : "";
  const place = item.place ? ` · ${item.place}` : "";
  return { name, detail: `${teacher}${place}` };
}

function ScheduleBoardInner() {
  const [classes, setClasses] = useState<Klass[]>([]);
  const [classId, setClassId] = useState("");
  const [week, setWeek] = useState("1");
  const [schedules, setSchedules] = useState<CourseSchedule[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [dragging, setDragging] = useState<DragPayload | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      listResource<Klass>(CLASS_RESOURCE, { sort: "-id" }),
      listResource<Topic>(TOPIC_RESOURCE, { filter: { status: "published" } }),
    ])
      .then(([ks, ts]) => {
        if (cancelled) return;
        setClasses(ks);
        if (ks[0]) setClassId(String(ks[0].id));
        setTopics(ts);
      })
      .catch(() => !cancelled && setError("基础数据加载失败"));
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

  const dropCell = useCallback(
    async (day: number, slot: number) => {
      if (!dragging || !classId) return;
      const klass = classes.find((k) => String(k.id) === classId);
      const slotDef = TIME_SLOTS[slot - 1];
      const base = {
        week_no: Number(week),
        day_of_week: day,
        place: klass?.default_room ?? "",
      };
      try {
        if (dragging.topicId != null) {
          const topic = topics.find((t) => t.id === dragging.topicId);
          await createRecord<CourseSchedule>(SCHEDULE_RESOURCE, {
            ...base,
            class_id: Number(classId),
            topic: dragging.topicId,
            topic_name: topic?.name ?? "",
            kind: "lecture",
            eval_enabled: true,
            status: "pending",
            start_time: `2026-01-${String(4 + day - 1).padStart(2, "0")}T${slotDef.start}:00.000Z`,
            end_time: `2026-01-${String(4 + day - 1).padStart(2, "0")}T${slotDef.end}:00.000Z`,
          });
          setNotice(`已排课：${topic?.name ?? ""} → 周${DAY_LABELS[day - 1]} ${slotDef.label}`);
        }
        if (dragging.scheduleId != null) {
          const item = schedules.find((s) => s.id === dragging.scheduleId);
          if (item) {
            const oldDay = item.day_of_week ?? dayFromTime(item.start_time);
            const oldSlot = slotFromTime(item.start_time, item.end_time);
            const oldText = `周${DAY_LABELS[oldDay - 1]} ${TIME_SLOTS[oldSlot - 1]?.label}`;
            const newText = `周${DAY_LABELS[day - 1]} ${slotDef.label}`;
            await updateRecord<CourseSchedule>(SCHEDULE_RESOURCE, item.id, {
              ...base,
              start_time: `2026-01-${String(4 + day - 1).padStart(2, "0")}T${slotDef.start}:00.000Z`,
              end_time: `2026-01-${String(4 + day - 1).padStart(2, "0")}T${slotDef.end}:00.000Z`,
            });
            await createRecord<Record<string, unknown>>(CHANGE_LOG_RESOURCE, {
              summary: `调课：${itemLabel(item).name} ${oldText} → ${newText}`,
              schedule: item.id,
              old_values: JSON.stringify({ day_of_week: oldDay, ...slotPick(oldSlot) }),
              new_values: JSON.stringify({ day_of_week: day, ...slotPick(slot) }),
              reason: "画布拖拽调课",
              notified: false,
            });
            setNotice(`已调课：${itemLabel(item).name} ${oldText} → ${newText}（已记录调课历史）`);
          }
        }
        setDragging(null);
        await load();
      } catch {
        setError("保存失败，请重试");
        setDragging(null);
      }
    },
    [dragging, classId, classes, week, topics, schedules, load],
  );

  const onDragStart = (payload: DragPayload) => (event: DragEvent) => {
    setDragging(payload);
    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setData("text/plain", JSON.stringify(payload));
  };

  const smartSchedule = useCallback(async () => {
    if (!classId) return;
    const klass = classes.find((k) => String(k.id) === classId);
    const taken = new Set(
      schedules.map(
        (s) => `${s.day_of_week ?? dayFromTime(s.start_time)}-${slotFromTime(s.start_time, s.end_time)}`,
      ),
    );
    const unscheduled = topics.filter((t) => !schedules.some((s) => resolveId(s.topic) === t.id));
    const created: string[] = [];
    for (const topic of unscheduled) {
      let placed = false;
      for (let slot = 1; slot <= TIME_SLOTS.length && !placed; slot++) {
        for (let day = 1; day <= 7 && !placed; day++) {
          const key = `${day}-${slot}`;
          if (taken.has(key)) continue;
          const slotDef = TIME_SLOTS[slot - 1];
          try {
            await createRecord<CourseSchedule>(SCHEDULE_RESOURCE, {
              class_id: Number(classId),
              topic: topic.id,
              topic_name: topic.name,
              kind: "lecture",
              week_no: Number(week),
              day_of_week: day,
              eval_enabled: true,
              status: "pending",
              place: klass?.default_room ?? "",
              start_time: `2026-01-${String(4 + day - 1).padStart(2, "0")}T${slotDef.start}:00.000Z`,
              end_time: `2026-01-${String(4 + day - 1).padStart(2, "0")}T${slotDef.end}:00.000Z`,
            });
            taken.add(key);
            created.push(`${topic.name}→周${DAY_LABELS[day - 1]}${slotDef.label}`);
            placed = true;
          } catch {
            setError("智能排课保存失败");
            return;
          }
        }
      }
    }
    setNotice(created.length > 0 ? `智能排课完成：${created.join("、")}` : "没有可排的空位或专题");
    await load();
  }, [classId, classes, schedules, topics, week, load]);

  const onDrop = (day: number, slot: number) => (event: DragEvent) => {
    event.preventDefault();
    void dropCell(day, slot);
  };

  const plannedCount = schedules.length;

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
        <Badge variant="secondary">本周已排 {plannedCount} 节</Badge>
        {conflicts.length > 0 && (
          <Badge variant="destructive">{conflicts.length} 处冲突，保存前请调整</Badge>
        )}
        <Button variant="outline" size="sm" onClick={() => void load()} disabled={loading}>
          刷新
        </Button>
        <Button size="sm" onClick={() => void smartSchedule()} disabled={loading}>
          智能排课（简化版）
        </Button>
      </div>

      {notice && <p className="text-sm text-primary">{notice}</p>}
      {error && <p className="text-sm text-destructive">{error}</p>}

      <div className="grid gap-4 lg:grid-cols-[280px_1fr]">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">专题池（拖拽排课）</CardTitle>
          </CardHeader>
          <CardContent className="flex max-h-[560px] flex-col gap-2 overflow-y-auto">
            {topics.length === 0 && (
              <p className="text-sm text-muted-foreground">暂无可排专题。</p>
            )}
            {topics.map((t) => {
              const scheduled = schedules.some((s) => resolveId(s.topic) === t.id);
              return (
                <div
                  key={t.id}
                  draggable
                  onDragStart={onDragStart({ topicId: t.id })}
                  className={`cursor-grab rounded-md border px-3 py-2 text-sm transition-colors hover:bg-accent ${
                    scheduled ? "opacity-50" : ""
                  }`}
                >
                  <div className="font-medium">{t.name}</div>
                  <div className="text-xs text-muted-foreground">
                    {t.hours ? `${t.hours} 学时` : ""} {t.teach_form ?? ""}
                    {scheduled ? " · 已排" : ""}
                  </div>
                </div>
              );
            })}
          </CardContent>
        </Card>

        {loading ? (
          <LoadingState />
        ) : (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">排课画布（拖动课程格子可调课）</CardTitle>
            </CardHeader>
            <CardContent className="overflow-x-auto">
              <div className="grid min-w-[720px] grid-cols-[90px_repeat(7,1fr)] gap-1">
                <div />
                {DAY_LABELS.map((d) => (
                  <div key={d} className="pb-1 text-center text-sm font-medium">
                    {d}
                  </div>
                ))}
                {TIME_SLOTS.map((slot) => (
                  <ScheduleRow
                    key={slot.key}
                    slot={slot}
                    cellMap={cellMap}
                    conflictKeys={conflictKeys}
                    dragging={dragging}
                    onDrop={onDrop}
                    onDragStart={onDragStart}
                  />
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

function slotPick(slot: number) {
  const s = TIME_SLOTS[slot - 1];
  return { start: s?.start, end: s?.end };
}


function ScheduleRow({
  slot,
  cellMap,
  conflictKeys,
  dragging,
  onDrop,
  onDragStart,
}: {
  slot: (typeof TIME_SLOTS)[number];
  cellMap: Map<string, CourseSchedule[]>;
  conflictKeys: Set<string>;
  dragging: DragPayload | null;
  onDrop: (day: number, slot: number) => (event: DragEvent) => void;
  onDragStart: (payload: DragPayload) => (event: DragEvent) => void;
}) {
  return (
    <>
      <div className="rounded-md bg-muted/60 px-2 py-2 text-xs">
        <div className="font-medium">{slot.label}</div>
        <div className="text-muted-foreground">
          {slot.start}–{slot.end}
        </div>
      </div>
      {DAY_LABELS.map((_, dayIdx) => {
        const day = dayIdx + 1;
        const key = `${day}-${slot.key}`;
        const items = cellMap.get(key) ?? [];
        const hasConflict = conflictKeys.has(key);
        return (
          <div
            key={key}
            onDragOver={(e) => {
              e.preventDefault();
              e.dataTransfer.dropEffect = "move";
            }}
            onDrop={onDrop(day, slot.key)}
            className={`min-h-[64px] rounded-md border p-1 transition-colors ${
              dragging ? "border-dashed" : ""
            } ${hasConflict ? "border-destructive bg-destructive/10" : "bg-background hover:bg-muted/40"}`}
          >
            {items.map((item) => {
              const { name, detail } = itemLabel(item);
              return (
                <div
                  key={item.id}
                  draggable
                  onDragStart={onDragStart({ scheduleId: item.id })}
                  className={`mb-1 cursor-grab rounded border px-2 py-1 text-xs ${
                    hasConflict ? "border-destructive bg-destructive/20" : "bg-muted/70"
                  }`}
                  title={detail}
                >
                  <div className="truncate font-medium">{name}</div>
                  <div className="truncate text-muted-foreground">{detail}</div>
                </div>
              );
            })}
            {items.length === 0 && (
              <div className="flex h-full items-center justify-center text-xs text-muted-foreground/40">
                拖入
              </div>
            )}
          </div>
        );
      })}
    </>
  );
}

export default function ScheduleBoardPage() {
  return (
    <PageErrorBoundary>
      <ScheduleBoardInner />
    </PageErrorBoundary>
  );
}
