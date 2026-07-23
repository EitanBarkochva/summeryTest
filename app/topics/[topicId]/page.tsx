import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { StudySite } from "../../StudySite";
import content from "../../studyContent.json";

type StudySection = {
  id: string;
  title: string;
};

const sections = content.sections as StudySection[];

type TopicPageProps = {
  params: Promise<{
    topicId: string;
  }>;
};

export function generateStaticParams() {
  return sections.map((section) => ({
    topicId: section.id,
  }));
}

export async function generateMetadata({
  params,
}: TopicPageProps): Promise<Metadata> {
  const { topicId } = await params;
  const section = sections.find((item) => item.id === topicId);

  if (!section) {
    return {
      title: content.title,
    };
  }

  return {
    title: `${section.title} | ${content.title}`,
    description: `חומר לימוד בנושא ${section.title} מתוך הסיכום בנוירוביולוגיה.`,
  };
}

export default async function TopicPage({ params }: TopicPageProps) {
  const { topicId } = await params;
  const section = sections.find((item) => item.id === topicId);

  if (!section) {
    notFound();
  }

  return <StudySite topicId={topicId} />;
}
