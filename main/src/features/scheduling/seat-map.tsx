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
  CLASS_RESOURCE,
  SEAT_RESOURCE,
  SEAT_ROOM_COLS,
  SEAT_ROOM_ROWS,
  STUDENT_RESOURCE,
  type Klass,
  type Seat,
  type SeatOrder,
  type Student,
  autoAssignSeats,
  createRecord,
  listResource,
  updateRecord,
} from "./api";

const ROWS = SEAT_ROOM_ROWS;
const COLS = SEAT_ROOM_COLS;

function studentLabel(student: Student | number | null | undefined): string {
  if (!student || typeof student === "number") return "";
  const nickname = typeof student.user === "object" ? student.user?.nickname : undefined;
  return student.name || nickname || "";
}

function SeatMapInner() {
  const [classes, setClasses] = useState<Klass[]>([]);
  const [classId, setClassId] = useState("");
  const [seats, setSeats] = useState<Seat[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [dragSeatId, setDragSeatId] = useState<number | null>(null);
  const [dragStudentId, setDragStudentId] = useState<number | null>(null);
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    let cancelled = false;
    listResource<Klass>(CLASS_RESOURCE, { sort: "-id" })
      .then((rows) => {
        if (cancelled) return;
        setClasses(rows);
        if (rows[0]) setClassId(String(rows[0].id));
      })
      .catch(() => !cancelled && setError("班次加载失败"));
    return () => {
      cancelled = true;
    };
  }, []);

  const load = useCallback(async () => {
    if (!classId) return;
    setLoading(true);
    setError(null);
    setNotice(null);
    setDirty(false);
    try {
      const [seatRows, studentRows] = await Promise.all([
        listResource<Seat>(SEAT_RESOURCE, {
          filter: { class_id: Number(classId) },
          appends: ["student"],
        }),
        listResource<Student>(STUDENT_RESOURCE, {
          filter: { class_id: Number(classId) },
          appends: ["user"],
        }),
      ]);
      setSeats(seatRows);
      setStudents(studentRows);
    } catch {
      setError("座位数据加载失败");
    } finally {
      setLoading(false);
    }
  }, [classId]);

  useEffect(() => {
    void load();
  }, [load]);

  const seatGrid = useMemo(() => {
    const map = new Map<string, Seat>();
    for (const seat of seats) {
      map.set(`${seat.row_no ?? 0}-${seat.col_no ?? 0}`, seat);
    }
    return map;
  }, [seats]);

  const assignedIds = useMemo(
    () =>
      new Set(
        seats
          .map((s) => (typeof s.student === "object" && s.student ? s.student.id : null))
          .filter((v): v is number => v != null),
      ),
    [seats],
  );

  const unassigned = useMemo(
    () => students.filter((s) => !assignedIds.has(s.id)),
    [students, assignedIds],
  );

  const updateSeat = (seatId: number, studentId: number | null) => {
    setSeats((prev) =>
      prev.map((s) =>
        s.id === seatId
          ? { ...s, student: studentId == null ? null : students.find((st) => st.id === studentId) ?? null }
          : s,
      ),
    );
    setDirty(true);
  };

  const onSeatDragStart = (seatId: number, hasStudent: boolean) => (event: DragEvent) => {
    if (!hasStudent) {
      event.preventDefault();
      return;
    }
    setDragSeatId(seatId);
    event.dataTransfer.effectAllowed = "move";
  };

  const onSeatDrop = (targetSeatId: number) => () => {
    if (dragStudentId != null) {
      updateSeat(targetSeatId, dragStudentId);
      setDragStudentId(null);
    } else if (dragSeatId != null && dragSeatId !== targetSeatId) {
      const from = seats.find((s) => s.id === dragSeatId);
      const to = seats.find((s) => s.id === targetSeatId);
      if (!from || !to) return;
      const fromStudent =
        typeof from.student === "object" && from.student ? from.student.id : null;
      const toStudent = typeof to.student === "object" && to.student ? to.student.id : null;
      updateSeat(dragSeatId, toStudent);
      updateSeat(targetSeatId, fromStudent);
      setDragSeatId(null);
    }
  };

  const onStudentDrop = (event: DragEvent) => {
    event.preventDefault();
    if (dragSeatId != null) {
      updateSeat(dragSeatId, null);
      setDragSeatId(null);
    }
  };

  const saveAll = useCallback(async () => {
    setSaving(true);
    setError(null);
    try {
      const current = await listResource<Seat>(SEAT_RESOURCE, {
        filter: { class_id: Number(classId) },
        appends: ["student"],
      });
      const changes: { id: number; student: number | null }[] = [];
      for (const seat of current) {
        const next = seats.find((s) => s.id === seat.id);
        if (!next) continue;
        const currentStudent =
          typeof seat.student === "object" && seat.student ? seat.student.id : null;
        const nextStudent =
          typeof next.student === "object" && next.student ? next.student.id : null;
        if (currentStudent !== nextStudent) {
          changes.push({ id: seat.id, student: nextStudent });
        }
      }
      await Promise.all(
        changes.map((c) => updateRecord<Seat>(SEAT_RESOURCE, c.id, { student: c.student })),
      );
      setNotice(`已保存 ${changes.length} 处座位调整`);
      setDirty(false);
      await load();
    } catch {
      setError("保存失败，请重试");
    } finally {
      setSaving(false);
    }
  }, [classId, seats, load]);

  const applyAutoAssign = async (order: SeatOrder) => {
    setError(null);
    try {
      const current = await listResource<Seat>(SEAT_RESOURCE, {
        filter: { class_id: Number(classId) },
        appends: ["student"],
      });
      const emptySeats = current.filter(
        (s) => !(typeof s.student === "object" && s.student),
      );
      const plan = autoAssignSeats(unassigned, emptySeats, order);
      if (plan.size === 0) {
        setNotice(unassigned.length === 0 ? "全部学员已排座" : "没有空位可自动排座");
        return;
      }
      setSeats((prev) =>
        prev.map((s) =>
          plan.has(s.id)
            ? { ...s, student: students.find((st) => st.id === plan.get(s.id)) ?? null }
            : s,
        ),
      );
      setDirty(true);
      setNotice(
        `已生成自动排座方案（按${order === "student_no" ? "学号" : "年龄"}顺序 ${plan.size} 人），点击保存生效`,
      );
    } catch {
      setError("自动排座失败，请重试");
    }
  };

  const assignedCount = students.length - unassigned.length;

  const initSeats = async () => {
    if (!classId) {
      setError("请先选择班次再初始化座位");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const created: Seat[] = [];
      for (let r = 1; r <= SEAT_ROOM_ROWS; r++) {
        for (let c = 1; c <= SEAT_ROOM_COLS; c++) {
          created.push(
            await createRecord<Seat>(SEAT_RESOURCE, {
              class_id: Number(classId),
              label: `${r}-${c}`,
              row_no: r,
              col_no: c,
              kind: "normal",
            }),
          );
        }
      }
      setNotice(`已初始化 ${created.length} 个座位，可开始排座`);
      await load();
    } catch {
      setError("座位初始化失败，请重试");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex flex-col gap-4 p-4">
      <div className="flex flex-wrap items-center gap-3">
        <Select
          value={classId}
          onValueChange={(v) => setClassId(v ?? "")}
          items={classes.map((k) => ({ value: String(k.id), label: k.name }))}
        >
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
        <Badge variant="secondary">
          已排座 {assignedCount}/{students.length}
        </Badge>
        <Button
          size="sm"
          variant="outline"
          onClick={() => void applyAutoAssign("student_no")}
          disabled={loading || saving}
        >
          按学号自动排座
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={() => void applyAutoAssign("birth_date")}
          disabled={loading || saving}
        >
          按年龄自动排座
        </Button>
        <Button size="sm" onClick={() => void saveAll()} disabled={!dirty || saving}>
          {saving ? "保存中…" : "保存排座"}
        </Button>
        <Button variant="outline" size="sm" onClick={() => void load()} disabled={loading}>
          刷新
        </Button>
      </div>

      {notice && <p className="text-sm text-primary">{notice}</p>}
      {error && <p className="text-sm text-destructive">{error}</p>}

      {!loading && seats.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center gap-3 py-6">
            <p className="text-sm text-muted-foreground">
              该班次还没有座位记录，先按教室布局（{SEAT_ROOM_ROWS} 排 × {SEAT_ROOM_COLS} 列）初始化。
            </p>
            <Button onClick={() => void initSeats()} disabled={saving}>
              {saving ? "初始化中…" : "初始化教室座位"}
            </Button>
          </CardContent>
        </Card>
      )}

      {loading ? (
        <LoadingState />
      ) : (
        <div className="grid gap-4 lg:grid-cols-[1fr_280px]">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">教室布局（拖动学员交换座位，拖到右侧未分配区可清空）</CardTitle>
            </CardHeader>
            <CardContent className="overflow-x-auto">
              <div className="mx-auto mb-2 text-center text-xs text-muted-foreground">
                讲台
              </div>
              <div
                className="grid min-w-[560px] gap-1"
                style={{ gridTemplateColumns: `40px repeat(${COLS}, minmax(56px, 1fr))` }}
              >
                <div />
                {Array.from({ length: COLS }, (_, c) => (
                  <div key={c} className="text-center text-xs text-muted-foreground">
                    第{c + 1}列
                  </div>
                ))}
                {Array.from({ length: ROWS }, (_, r) => (
                  <SeatRowCells
                    key={r}
                    row={r}
                    seatGrid={seatGrid}
                    onSeatDragStart={onSeatDragStart}
                    onSeatDrop={onSeatDrop}
                  />
                ))}
              </div>
            </CardContent>
          </Card>

          <Card
            onDragOver={(e) => {
              e.preventDefault();
              e.dataTransfer.dropEffect = "move";
            }}
            onDrop={onStudentDrop}
          >
            <CardHeader>
              <CardTitle className="text-base">未分配学员（{unassigned.length}）</CardTitle>
            </CardHeader>
            <CardContent className="flex max-h-[480px] flex-col gap-2 overflow-y-auto">
              {unassigned.length === 0 && (
                <p className="text-sm text-muted-foreground">全部学员已排座。</p>
              )}
              {unassigned.map((s) => (
                <div
                  key={s.id}
                  draggable
                  onDragStart={(e) => {
                    setDragStudentId(s.id);
                    e.dataTransfer.effectAllowed = "move";
                  }}
                  className="cursor-grab rounded-md border px-3 py-2 text-sm hover:bg-accent"
                >
                  <div className="font-medium">{studentLabel(s) || `学员 #${s.id}`}</div>
                  <div className="text-xs text-muted-foreground">
                    {s.student_no ? `学号 ${s.student_no}` : ""} {s.birth_date ?? ""}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

function SeatRowCells({
  row,
  seatGrid,
  onSeatDragStart,
  onSeatDrop,
}: {
  row: number;
  seatGrid: Map<string, Seat>;
  onSeatDragStart: (seatId: number, hasStudent: boolean) => (event: DragEvent) => void;
  onSeatDrop: (seatId: number) => (event: DragEvent) => void;
}) {
  return (
    <>
      <div className="flex items-center justify-center text-xs text-muted-foreground">
        第{row + 1}排
      </div>
      {Array.from({ length: COLS }, (_, c) => {
        const seat = seatGrid.get(`${row + 1}-${c + 1}`);
        const student =
          seat && typeof seat.student === "object" && seat.student ? seat.student : null;
        return (
          <div
            key={c}
            draggable={!!student}
            onDragStart={onSeatDragStart(seat?.id ?? 0, !!student)}
            onDragOver={(e) => {
              e.preventDefault();
              e.dataTransfer.dropEffect = "move";
            }}
            onDrop={onSeatDrop(seat?.id ?? 0)}
            className={`flex h-[48px] flex-col items-center justify-center rounded-md border px-1 text-center text-xs ${
              student
                ? "cursor-grab border-primary/60 bg-primary/10"
                : "border-dashed bg-background text-muted-foreground/50 hover:bg-muted/40"
            }`}
          >
            {student ? (
              <>
                <div className="w-full truncate font-medium">{studentLabel(student)}</div>
                <div className="w-full truncate text-[10px] text-muted-foreground">
                  {seat?.label ?? `${row + 1}-${c + 1}`}
                </div>
              </>
            ) : (
              <div>{seat?.label ?? `${row + 1}-${c + 1}`}</div>
            )}
          </div>
        );
      })}
    </>
  );
}

export default function SeatMapPage() {
  return (
    <PageErrorBoundary>
      <SeatMapInner />
    </PageErrorBoundary>
  );
}
