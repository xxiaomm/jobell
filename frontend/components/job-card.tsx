import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import type { Job } from "@/lib/api";

export function JobCard({ job }: { job: Job }) {
  return (
    <Link href={`/jobs/${job.id}`}>
      <Card className="transition-colors hover:border-primary">
        <CardHeader>
          <CardTitle>{job.title}</CardTitle>
          <CardDescription>
            {job.company.name}
            {job.location ? ` · ${job.location}` : ""}
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          <Badge variant="secondary">{job.level}</Badge>
          {job.degree_requirement !== "none" && <Badge variant="secondary">{job.degree_requirement}+</Badge>}
          {job.min_years_experience != null && <Badge variant="outline">{job.min_years_experience}+ yrs</Badge>}
          {job.posted_at && (
            <span className="ml-auto self-center text-xs text-muted-foreground">
              {new Date(job.posted_at).toLocaleDateString()}
            </span>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}
