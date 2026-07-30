import { notFound } from "next/navigation";
import type { Metadata } from "next";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { getJob } from "@/lib/api";

interface JobPageProps {
  params: { id: string };
}

async function fetchJob(id: string) {
  try {
    return await getJob(Number(id));
  } catch {
    return null;
  }
}

export async function generateMetadata({ params }: JobPageProps): Promise<Metadata> {
  const job = await fetchJob(params.id);
  if (!job) return { title: "Job not found — Jobell" };
  return {
    title: `${job.title} at ${job.company.name} — Jobell`,
    description: `${job.title} at ${job.company.name}${job.location ? ` (${job.location})` : ""}. Apply now on Jobell.`,
  };
}

export default async function JobPage({ params }: JobPageProps) {
  const job = await fetchJob(params.id);
  if (!job) notFound();

  return (
    <article className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">{job.title}</h1>
        <p className="text-muted-foreground">
          {job.company.name}
          {job.location ? ` · ${job.location}` : ""}
          {job.department ? ` · ${job.department}` : ""}
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        <Badge variant="secondary">{job.level}</Badge>
        {job.degree_requirement !== "none" && <Badge variant="secondary">{job.degree_requirement}+</Badge>}
        {job.min_years_experience != null && <Badge variant="outline">{job.min_years_experience}+ yrs experience</Badge>}
      </div>

      {job.posted_at && (
        <p className="text-sm text-muted-foreground">Posted {new Date(job.posted_at).toLocaleDateString()}</p>
      )}

      <Button asChild size="lg">
        <a href={job.url} target="_blank" rel="noreferrer">
          Apply on {job.company.name}&apos;s site
        </a>
      </Button>
    </article>
  );
}
