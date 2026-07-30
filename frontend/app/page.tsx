import { JobCard } from "@/components/job-card";
import { JobFilters } from "@/components/job-filters";
import { Button } from "@/components/ui/button";
import { getJobs, type DegreeRequirement, type JobLevel } from "@/lib/api";

interface HomeProps {
  searchParams: Record<string, string | undefined>;
}

export default async function Home({ searchParams }: HomeProps) {
  const page = Number(searchParams.page ?? "1");

  const { items, total, page_size } = await getJobs({
    title: searchParams.title,
    location: searchParams.location,
    level: searchParams.level as JobLevel | undefined,
    min_years: searchParams.min_years ? Number(searchParams.min_years) : undefined,
    degree: searchParams.degree as DegreeRequirement | undefined,
    posted_after: searchParams.posted_after,
    page,
  });

  const totalPages = Math.max(1, Math.ceil(total / page_size));

  return (
    <div className="space-y-6">
      <JobFilters />

      <p className="text-sm text-muted-foreground">{total} jobs found</p>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {items.map((job) => (
          <JobCard key={job.id} job={job} />
        ))}
      </div>

      {items.length === 0 && (
        <p className="text-center text-muted-foreground">No jobs match these filters yet — try widening them.</p>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
            <Button key={p} variant={p === page ? "default" : "outline"} size="sm" asChild>
              <a href={`?${new URLSearchParams({ ...searchParams, page: String(p) } as Record<string, string>).toString()}`}>
                {p}
              </a>
            </Button>
          ))}
        </div>
      )}
    </div>
  );
}
