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
