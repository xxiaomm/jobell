"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const LEVELS = ["intern", "junior", "mid", "senior", "staff"] as const;
const DEGREES = ["none", "bachelor", "master", "phd"] as const;
const POSTED_WITHIN_DAYS = [
  { label: "Any time", value: "any" },
  { label: "Past 24 hours", value: "1" },
  { label: "Past 3 days", value: "3" },
  { label: "Past week", value: "7" },
  { label: "Past month", value: "30" },
];

export function JobFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [title, setTitle] = useState(searchParams.get("title") ?? "");
  const [location, setLocation] = useState(searchParams.get("location") ?? "");
  const [level, setLevel] = useState(searchParams.get("level") ?? "any");
  const [minYears, setMinYears] = useState(searchParams.get("min_years") ?? "");
  const [degree, setDegree] = useState(searchParams.get("degree") ?? "any");
  const [postedWithin, setPostedWithin] = useState("any");

  function applyFilters(e: React.FormEvent) {
    e.preventDefault();
    const params = new URLSearchParams();
    if (title) params.set("title", title);
    if (location) params.set("location", location);
    if (level !== "any") params.set("level", level);
    if (minYears) params.set("min_years", minYears);
    if (degree !== "any") params.set("degree", degree);
    if (postedWithin !== "any") {
      const since = new Date();
      since.setDate(since.getDate() - Number(postedWithin));
      params.set("posted_after", since.toISOString());
    }
    router.push(`/?${params.toString()}`);
  }

  return (
    <form onSubmit={applyFilters} className="grid grid-cols-1 gap-4 rounded-lg border bg-card p-4 sm:grid-cols-2 lg:grid-cols-5">
      <div className="space-y-1.5">
        <Label htmlFor="title">Title</Label>
        <Input id="title" placeholder="e.g. Software Engineer" value={title} onChange={(e) => setTitle(e.target.value)} />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="location">Location</Label>
        <Input id="location" placeholder="e.g. Remote, SF" value={location} onChange={(e) => setLocation(e.target.value)} />
      </div>

      <div className="space-y-1.5">
        <Label>Level</Label>
        <Select value={level} onValueChange={setLevel}>
          <SelectTrigger>
            <SelectValue placeholder="Any level" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="any">Any level</SelectItem>
            {LEVELS.map((l) => (
              <SelectItem key={l} value={l}>
                {l}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="min_years">Max years required</Label>
        <Input
          id="min_years"
          type="number"
          min={0}
          placeholder="e.g. 3"
          value={minYears}
          onChange={(e) => setMinYears(e.target.value)}
        />
      </div>

      <div className="space-y-1.5">
        <Label>Degree</Label>
        <Select value={degree} onValueChange={setDegree}>
          <SelectTrigger>
            <SelectValue placeholder="Any degree" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="any">Any degree</SelectItem>
            {DEGREES.map((d) => (
              <SelectItem key={d} value={d}>
                {d}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-1.5">
        <Label>Posted</Label>
        <Select value={postedWithin} onValueChange={setPostedWithin}>
          <SelectTrigger>
            <SelectValue placeholder="Any time" />
          </SelectTrigger>
          <SelectContent>
            {POSTED_WITHIN_DAYS.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="sm:col-span-2 lg:col-span-5">
        <Button type="submit">Apply filters</Button>
      </div>
    </form>
  );
}
