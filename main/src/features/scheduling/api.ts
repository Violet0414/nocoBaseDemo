import { nocobaseClient } from "@nocobase/portal-sdk/client";

export const CLASS_RESOURCE = "nb_dx_class";
export const SCHEDULE_RESOURCE = "nb_dx_course_schedule";
export const SEAT_RESOURCE = "nb_dx_seat";
export const STUDENT_RESOURCE = "nb_dx_student";
export const TOPIC_RESOURCE = "nb_dx_topic";
export const TEACHING_PLAN_RESOURCE = "nb_dx_teaching_plan";
export const CHANGE_LOG_RESOURCE = "nb_dx_change_log";

export interface Klass {
  id: number;
  name: string;
  start_date?: string | null;
  end_date?: string | null;
  total_days?: number | null;
  default_room?: string | null;
  qr_token?: string | null;
}

export interface Topic {
  id: number;
  name: string;
  hours?: number | null;
  teach_form?: string | null;
  category?: string | null;
  status?: string | null;
}

export interface TeacherRef {
  id: number;
  name: string;
}

export interface CourseSchedule {
  id: number;
  topic_name?: string | null;
  class?: { id: number; name: string } | number | null;
  topic?: Topic | number | null;
  kind?: string | null;
  week_no?: number | null;
  day_of_week?: number | null;
  start_time?: string | null;
  end_time?: string | null;
  place?: string | null;
  teacher?: TeacherRef | number | null;
  status?: string | null;
}

export interface Seat {
  id: number;
  label?: string | null;
  class?: { id: number } | number | null;
  student?: Student | number | null;
  room?: string | null;
  row_no?: number | null;
  col_no?: number | null;
  kind?: string | null;
}

export interface Student {
  id: number;
  name?: string | null;
  student_no?: string | null;
  birth_date?: string | null;
  gender?: string | null;
  user?: { id: number; nickname?: string | null } | number | null;
}

export interface ChangeLog {
  id: number;
  summary?: string | null;
  schedule?: number | null;
  old_values?: string | null;
  new_values?: string | null;
  reason?: string | null;
  operator?: number | null;
  notified?: boolean | null;
}

export const TIME_SLOTS = [
  { key: 1, label: "上午第1节", start: "08:30", end: "10:10" },
  { key: 2, label: "上午第2节", start: "10:30", end: "12:10" },
  { key: 3, label: "下午第1节", start: "14:00", end: "15:40" },
  { key: 4, label: "下午第2节", start: "16:00", end: "17:40" },
  { key: 5, label: "晚间", start: "19:00", end: "20:40" },
];

export const DAY_LABELS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];

export const SEAT_ROOM_ROWS = 6;
export const SEAT_ROOM_COLS = 8;

export async function listResource<T>(
  resource: string,
  query: { filter?: Record<string, unknown>; appends?: string[]; pageSize?: number; sort?: string },
): Promise<T[]> {
  const q: Record<string, string | number> = { pageSize: query.pageSize ?? 200 };
  if (query.filter && Object.keys(query.filter).length > 0) {
    q.filter = JSON.stringify(query.filter);
  }
  if (query.appends?.length) {
    q.appends = query.appends.join(",");
  }
  if (query.sort) {
    q.sort = query.sort;
  }
  // nocobaseClient.action 默认 unwrap:"data"，返回的已是 payload.data 本体
  const res = await nocobaseClient.action<T[] | { data?: T[] }>(resource, "list", { query: q });
  return Array.isArray(res) ? res : (res?.data ?? []);
}

export async function createRecord<T>(resource: string, body: Record<string, unknown>): Promise<T> {
  const res = await nocobaseClient.action<T | { data?: T }>(resource, "create", { method: "POST", body });
  if (res && typeof res === "object" && "data" in (res as { data?: T })) {
    return (res as { data: T }).data;
  }
  return res as T;
}

export async function updateRecord<T>(resource: string, id: number, body: Record<string, unknown>): Promise<T> {
  const res = await nocobaseClient.action<T[] | { data?: T[] }>(resource, "update", {
    method: "POST",
    query: { filterByTk: id },
    body,
  });
  const row = Array.isArray(res) ? res[0] : (res?.data?.[0] ?? res?.data);
  return row as T;
}

export function resolveId(value: { id: number } | number | null | undefined): number | null {
  if (value == null) return null;
  return typeof value === "number" ? value : value.id;
}

export function slotKey(day: number, slot: number): string {
  return `${day}-${slot}`;
}

export function dayFromTime(time?: string | null): number {
  if (!time) return 1;
  const d = new Date(time).getDay();
  return d === 0 ? 7 : d;
}

export function slotFromTime(time?: string | null, end?: string | null): number {
  if (!time) return 1;
  const hhmm = new Date(time).toTimeString().slice(0, 5);
  const slot = TIME_SLOTS.find((s) => hhmm >= s.start && hhmm < s.end);
  if (slot) return slot.key;
  const endHhmm = end ? new Date(end).toTimeString().slice(0, 5) : hhmm;
  return TIME_SLOTS.find((s) => hhmm >= s.start || endHhmm > s.start)?.key ?? 1;
}

export interface Conflict {
  day: number;
  slot: number;
  reason: string;
  ids: number[];
}

function overlaps(a: CourseSchedule, b: CourseSchedule): boolean {
  if ((a.week_no ?? 0) !== (b.week_no ?? 0)) return false;
  if ((a.day_of_week ?? dayFromTime(a.start_time)) !== (b.day_of_week ?? dayFromTime(b.start_time))) return false;
  const aStart = slotFromTime(a.start_time, a.end_time);
  const bStart = slotFromTime(b.start_time, b.end_time);
  if (aStart !== bStart) return false;
  return true;
}

export function detectConflicts(items: CourseSchedule[]): Conflict[] {
  const conflicts = new Map<string, Conflict>();
  for (let i = 0; i < items.length; i++) {
    for (let j = i + 1; j < items.length; j++) {
      const a = items[i];
      const b = items[j];
      if (!overlaps(a, b)) continue;
      const day = a.day_of_week ?? dayFromTime(a.start_time);
      const slot = slotFromTime(a.start_time, a.end_time);
      const key = `${day}-${slot}`;
      const teacherA = resolveId(a.teacher);
      const teacherB = resolveId(b.teacher);
      const placeA = a.place ?? "";
      const placeB = b.place ?? "";
      let reason = "";
      if (teacherA && teacherA === teacherB) reason = `同一教师同时段被重复安排（${(a.teacher as TeacherRef)?.name ?? ""}）`;
      else if (placeA && placeA === placeB) reason = `同一教室同时段冲突（${placeA}）`;
      if (!reason) continue;
      const existing = conflicts.get(key);
      if (existing) {
        existing.ids.push(a.id, b.id);
        continue;
      }
      conflicts.set(key, { day, slot, reason, ids: [a.id, b.id] });
    }
  }
  return Array.from(conflicts.values());
}

export type SeatOrder = "student_no" | "birth_date";

export function autoAssignSeats(students: Student[], emptySeats: Seat[], order: SeatOrder): Map<number, number> {
  const sorted = [...students].sort((a, b) => {
    if (order === "birth_date") {
      const da = a.birth_date ?? "9999-12-31";
      const db = b.birth_date ?? "9999-12-31";
      return da.localeCompare(db);
    }
    return (a.student_no ?? "").localeCompare(b.student_no ?? "", "zh-CN", { numeric: true });
  });
  const seats = [...emptySeats].sort((a, b) => {
    const r = (a.row_no ?? 0) - (b.row_no ?? 0);
    return r !== 0 ? r : (a.col_no ?? 0) - (b.col_no ?? 0);
  });
  const plan = new Map<number, number>();
  const n = Math.min(sorted.length, seats.length);
  for (let i = 0; i < n; i++) {
    plan.set(seats[i].id, sorted[i].id);
  }
  return plan;
}
