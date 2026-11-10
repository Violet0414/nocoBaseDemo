import { describe, expect, it } from "vitest";

import {
  autoAssignSeats,
  detectConflicts,
  type CourseSchedule,
  type Seat,
  type Student,
} from "@/features/scheduling/api";

function schedule(partial: Partial<CourseSchedule>): CourseSchedule {
  return { id: 0, ...partial } as CourseSchedule;
}

describe("detectConflicts", () => {
  it("flags the same teacher in the same slot", () => {
    const items = [
      schedule({ id: 1, week_no: 1, day_of_week: 1, start_time: "2026-01-05T08:30:00Z", teacher: { id: 9, name: "张" } }),
      schedule({ id: 2, week_no: 1, day_of_week: 1, start_time: "2026-01-05T09:00:00Z", teacher: { id: 9, name: "张" } }),
    ];
    const conflicts = detectConflicts(items);
    expect(conflicts).toHaveLength(1);
    expect(conflicts[0].reason).toContain("同一教师");
    expect(conflicts[0].ids).toEqual([1, 2]);
  });

  it("flags the same place in the same slot", () => {
    const items = [
      schedule({ id: 1, week_no: 1, day_of_week: 2, start_time: "2026-01-06T14:00:00Z", place: "一教201" }),
      schedule({ id: 2, week_no: 1, day_of_week: 2, start_time: "2026-01-06T14:30:00Z", place: "一教201" }),
    ];
    const conflicts = detectConflicts(items);
    expect(conflicts).toHaveLength(1);
    expect(conflicts[0].reason).toContain("同一教室");
  });

  it("does not flag different slots", () => {
    const items = [
      schedule({ id: 1, week_no: 1, day_of_week: 1, start_time: "2026-01-05T08:30:00Z", place: "一教201" }),
      schedule({ id: 2, week_no: 1, day_of_week: 1, start_time: "2026-01-05T10:30:00Z", place: "一教201" }),
    ];
    expect(detectConflicts(items)).toHaveLength(0);
  });

  it("does not flag same teacher in different weeks", () => {
    const items = [
      schedule({ id: 1, week_no: 1, day_of_week: 1, start_time: "2026-01-05T08:30:00Z", teacher: { id: 9, name: "张" } }),
      schedule({ id: 2, week_no: 2, day_of_week: 1, start_time: "2026-01-05T08:30:00Z", teacher: { id: 9, name: "张" } }),
    ];
    expect(detectConflicts(items)).toHaveLength(0);
  });

  it("flags class-slot duplication even with different teachers and places", () => {
    const items = [
      schedule({ id: 1, week_no: 1, day_of_week: 1, start_time: "2026-01-05T08:30:00Z", teacher: { id: 1, name: "甲" }, place: "一教101" }),
      schedule({ id: 2, week_no: 1, day_of_week: 1, start_time: "2026-01-05T08:30:00Z", teacher: { id: 2, name: "乙" }, place: "一教102" }),
    ];
    const conflicts = detectConflicts(items);
    expect(conflicts).toHaveLength(1);
    expect(conflicts[0].reason).toContain("班级同时段");
    expect(conflicts[0].reason).toContain("2 节");
  });

  it("counts deduplicated courses for a 10-course same-slot pile", () => {
    const items = Array.from({ length: 10 }, (_, k) =>
      schedule({
        id: k + 1,
        week_no: 1,
        day_of_week: 3,
        start_time: "2026-01-07T08:30:00Z",
        teacher: { id: k + 1, name: `师${k + 1}` },
        place: `教室${k + 1}`,
      })
    );
    const conflicts = detectConflicts(items);
    expect(conflicts).toHaveLength(1);
    expect(conflicts[0].reason).toContain("10 节");
    expect(new Set(conflicts[0].ids).size).toBe(10);
  });

  it("keeps teacher reason priority when teacher collides inside a pile", () => {
    const items = [
      schedule({ id: 1, week_no: 1, day_of_week: 4, start_time: "2026-01-08T08:30:00Z", teacher: { id: 7, name: "李" }, place: "A" }),
      schedule({ id: 2, week_no: 1, day_of_week: 4, start_time: "2026-01-08T08:30:00Z", teacher: { id: 8, name: "王" }, place: "B" }),
      schedule({ id: 3, week_no: 1, day_of_week: 4, start_time: "2026-01-08T08:30:00Z", teacher: { id: 7, name: "李" }, place: "C" }),
    ];
    const conflicts = detectConflicts(items);
    expect(conflicts).toHaveLength(1);
    expect(conflicts[0].reason).toContain("同一教师");
  });
});

describe("autoAssignSeats", () => {
  const students: Student[] = [
    { id: 3, student_no: "S2026003", birth_date: "1990-01-01" },
    { id: 1, student_no: "S2026001", birth_date: "1985-05-05" },
    { id: 2, student_no: "S2026002", birth_date: "1992-10-10" },
  ];

  const seats: Seat[] = [
    { id: 11, row_no: 2, col_no: 1 } as Seat,
    { id: 10, row_no: 1, col_no: 2 } as Seat,
    { id: 9, row_no: 1, col_no: 1 } as Seat,
  ];

  it("assigns seats row by row ordered by student_no", () => {
    const plan = autoAssignSeats(students, seats, "student_no");
    expect(plan.get(9)).toBe(1);
    expect(plan.get(10)).toBe(2);
    expect(plan.get(11)).toBe(3);
  });

  it("assigns seats ordered by birth_date (oldest first)", () => {
    const plan = autoAssignSeats(students, seats, "birth_date");
    expect(plan.get(9)).toBe(1);
    expect(plan.get(10)).toBe(3);
    expect(plan.get(11)).toBe(2);
  });

  it("stops when there are more students than seats", () => {
    const smallSeats = seats.slice(0, 2);
    const plan = autoAssignSeats(students, smallSeats, "student_no");
    expect(plan.size).toBe(2);
  });
});
