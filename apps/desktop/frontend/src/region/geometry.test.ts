import { describe, expect, it } from "vitest";
import {
  letterboxView,
  projectRegionBox,
  projectRegionPolygon,
} from "./geometry";
import type { NormalizedRegionGeometry } from "./types";

/**
 * The single projection math pins (M2-WORKBENCH-REACT-1). These tests are
 * the executable statement of the two M2-UI1 §2.2 RegionOverlay hard rules:
 * size only from the projection (letterboxView input), only normalized
 * values crossing the boundary (geometry input domain 0..1).
 */

const PAGE_16_9 = { width: 1600, height: 900 };

describe("letterboxView (size only from the projection)", () => {
  it("centers an aspect-preserving view inside a wider container", () => {
    // container 2000x1000 (2:1) is wider than the 16:9 page: the view fits
    // by height (scale 1000/900), centered horizontally
    const view = letterboxView(PAGE_16_9, 2000, 1000);
    expect(view.x).toBeCloseTo(111.111, 3);
    expect(view.y).toBe(0);
    expect(view.width).toBeCloseTo(1777.778, 3);
    expect(view.height).toBe(1000);
  });

  it("fits by width when the container is proportionally taller", () => {
    // container 800x900: scale = 800/1600 = 0.5, centered vertically
    const view = letterboxView(PAGE_16_9, 800, 900);
    expect(view).toEqual({ x: 0, y: 225, width: 800, height: 450 });
  });

  it("collapses to an empty rect when no page projection exists (null)", () => {
    expect(letterboxView(null, 800, 600)).toEqual({
      x: 0, y: 0, width: 0, height: 0,
    });
  });

  it("collapses on degenerate extents (zero page or container)", () => {
    expect(letterboxView({ width: 0, height: 900 }, 800, 600).width).toBe(0);
    expect(letterboxView(PAGE_16_9, 0, 600).width).toBe(0);
  });
});

describe("projectRegionBox (normalized in, viewport pixels out)", () => {
  const GEOMETRY: NormalizedRegionGeometry = {
    bbox: [0.25, 0.5, 0.25, 0.25],
    polygon: [],
  };

  it("maps the normalized domain onto the letterbox rect, not the container", () => {
    // view = {x:111.11, y:0, w:1777.78, h:1000}: a normalized 0.25 x lands
    // at 111.11 + 0.25*1777.78 = 555.56
    const view = letterboxView(PAGE_16_9, 2000, 1000);
    const box = projectRegionBox(GEOMETRY, view);
    expect(box.x).toBeCloseTo(555.556, 3);
    expect(box.y).toBe(500);
    expect(box.width).toBeCloseTo(444.444, 3);
    expect(box.height).toBe(250);
  });

  it("keeps frames glued to the image at any container size (same math, new view)", () => {
    const narrow = letterboxView(PAGE_16_9, 800, 900);
    const box = projectRegionBox(GEOMETRY, narrow);
    // normalized 0.25 x of the 800-wide image area + no x offset; the y
    // carries the view offset (225 + 0.5*450)
    expect(box).toEqual({ x: 200, y: 450, width: 200, height: 112.5 });
  });
});

describe("projectRegionPolygon", () => {
  it("projects every ring point through the same view", () => {
    const geometry: NormalizedRegionGeometry = {
      bbox: [0, 0, 1, 1],
      polygon: [[0, 0], [1, 0], [1, 1], [0, 1]],
    };
    const view = letterboxView(PAGE_16_9, 2000, 1000);
    const points = projectRegionPolygon(geometry, view);
    expect(points.length).toBe(4);
    expect(points[0][0]).toBeCloseTo(111.111, 3);
    expect(points[0][1]).toBe(0);
    expect(points[1][0]).toBeCloseTo(1888.889, 3);
    expect(points[2][1]).toBe(1000);
  });

  it("keeps an empty ring empty", () => {
    const geometry: NormalizedRegionGeometry = {
      bbox: [0.1, 0.1, 0.1, 0.1],
      polygon: [],
    };
    expect(
      projectRegionPolygon(geometry, letterboxView(PAGE_16_9, 2000, 1000)),
    ).toEqual([]);
  });
});
