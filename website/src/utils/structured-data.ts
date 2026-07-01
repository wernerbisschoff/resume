/**
 * Structured Data Utilities
 *
 * Generates JSON-LD schema.org structured data for SEO.
 * Single source of truth for all schemas - import from pages to ensure consistency.
 *
 * Identity model: a single @id-graph anchored at `${siteUrl}#person`. Every other
 * entity (Occupation, AlumniOf, Credential, WebSite, ProfilePage, FAQPage) is
 * either the same node or references it by @id, so Google resolves a single
 * canonical entity for "Werner Bisschoff" instead of fragments.
 */

import { CONTACT_INFO } from '~/config/contact';
import type { CollectionEntry } from 'astro:content';

// ---------------------------------------------------------------------------
// Canonical @id-graph anchors
// ---------------------------------------------------------------------------

const id = {
  person: `${CONTACT_INFO.siteUrl}#person`,
  occupation: `${CONTACT_INFO.siteUrl}#occupation`,
  alumni: `${CONTACT_INFO.siteUrl}#alumni`,
  credential: `${CONTACT_INFO.siteUrl}#credential`,
  workLocation: `${CONTACT_INFO.siteUrl}#work-location`,
  website: `${CONTACT_INFO.siteUrl}#website`,
  profilePage: `${CONTACT_INFO.siteUrl}#profile`,
  faqPage: `${CONTACT_INFO.siteUrl}#faq`,
  contactPage: `${CONTACT_INFO.siteUrl}#contact`,
} as const;

const sameAsUrls = [
  CONTACT_INFO.social.github.url,
  CONTACT_INFO.social.linkedin.url,
  ...(CONTACT_INFO.social.twitter ? [CONTACT_INFO.social.twitter.url] : []),
];

// ---------------------------------------------------------------------------
// Person — the canonical entity
// ---------------------------------------------------------------------------

/**
 * Generate Person schema with full @id-graph for entity disambiguation.
 * Uses every known signals Google uses to anchor a named entity:
 *   - @id, @type
 *   - name, givenName, familyName
 *   - jobTitle, description
 *   - url, image, email, telephone (none → omitted)
 *   - address (PostalAddress)
 *   - workLocation (Place)
 *   - alumniOf (EducationalOrganization)
 *   - hasCredential (EducationalOccupationalCredential)
 *   - hasOccupation (Occupation) — the role/position node
 *   - knowsAbout (Subject keywords for query matching)
 *   - knowsLanguage (Language)
 *   - nationality (Country)
 *   - sameAs (canonical social profile URLs)
 *   - seeks (Demand) — contract availability
 */
export const getPersonSchema = (): object => ({
  '@id': id.person,
  '@context': 'https://schema.org',
  '@type': 'Person',
  name: CONTACT_INFO.name,
  givenName: 'Werner',
  familyName: 'Bisschoff',
  alternateName: ['W. Bisschoff', 'Werner Bisschof'],
  jobTitle: CONTACT_INFO.jobTitle,
  description:
    `${CONTACT_INFO.name} is a software engineer based in ${CONTACT_INFO.location}, ` +
    `${CONTACT_INFO.country}, specializing in embedded systems, systems engineering, ` +
    `infrastructure engineering, test-driven development, and agentic AI workflows.`,
  url: CONTACT_INFO.siteUrl,
  image: `${CONTACT_INFO.siteUrl}/images/werner-bisschoff-software-engineer.webp`,
  email: CONTACT_INFO.email,
  address: {
    '@type': 'PostalAddress',
    addressLocality: CONTACT_INFO.location,
    addressRegion: 'Western Cape',
    addressCountry: CONTACT_INFO.country,
  },
  workLocation: { '@id': id.workLocation },
  alumniOf: { '@id': id.alumni },
  hasCredential: { '@id': id.credential },
  hasOccupation: { '@id': id.occupation },
  knowsAbout: CONTACT_INFO.expertise,
  knowsLanguage: ['en', 'af'],
  nationality: { '@type': 'Country', name: CONTACT_INFO.country },
  sameAs: sameAsUrls,
  seeks: CONTACT_INFO.availability,
});

// ---------------------------------------------------------------------------
// WorkLocation — Place node referenced from Person.workLocation
// ---------------------------------------------------------------------------

export const getWorkLocationSchema = (): object => ({
  '@id': id.workLocation,
  '@context': 'https://schema.org',
  '@type': 'Place',
  name: CONTACT_INFO.location,
  address: {
    '@type': 'PostalAddress',
    addressLocality: CONTACT_INFO.location,
    addressRegion: 'Western Cape',
    addressCountry: CONTACT_INFO.country,
  },
});

// ---------------------------------------------------------------------------
// Occupation — Role node referenced from Person.hasOccupation
// ---------------------------------------------------------------------------

export const getOccupationSchema = (): object => ({
  '@id': id.occupation,
  '@context': 'https://schema.org',
  '@type': 'Occupation',
  name: CONTACT_INFO.jobTitle,
  description:
    'Software engineering across embedded systems, infrastructure, and agentic AI workflows ' +
    'with spec-driven, test-driven development practices.',
  occupationLocation: { '@id': id.workLocation },
  skills: CONTACT_INFO.expertise,
  responsibilities: [
    'Design and implement embedded firmware (ESP32, FreeRTOS)',
    'Build and operate cloud infrastructure (AWS, Docker, Pulumi)',
    'Develop agentic AI workflows and tooling',
    'Practice test-driven development across the stack',
  ],
  estimatedSalary: {
    '@type': 'MonetaryAmountDistribution',
    name: 'Open to negotiation',
    currency: 'USD',
  },
});

// ---------------------------------------------------------------------------
// AlumniOf — EducationalOrganization node referenced from Person.alumniOf
// ---------------------------------------------------------------------------

export const getAlumniSchema = (): object => ({
  '@id': id.alumni,
  '@context': 'https://schema.org',
  '@type': 'EducationalOrganization',
  name: CONTACT_INFO.education.school,
  address: {
    '@type': 'PostalAddress',
    addressCountry: CONTACT_INFO.country,
  },
  alumni: { '@id': id.person },
});

// ---------------------------------------------------------------------------
// HasCredential — EducationalOccupationalCredential node
// ---------------------------------------------------------------------------

export const getCredentialSchema = (): object => ({
  '@id': id.credential,
  '@context': 'https://schema.org',
  '@type': 'EducationalOccupationalCredential',
  name: CONTACT_INFO.education.degree,
  credentialCategory: 'degree',
  about: {
    '@type': 'Course',
    name: CONTACT_INFO.education.field,
  },
  recognizedBy: { '@id': id.alumni },
  dateCompleted: String(CONTACT_INFO.education.year),
});

// ---------------------------------------------------------------------------
// ProfilePage — schema for the homepage as a profile page (LinkedIn competitor)
// ---------------------------------------------------------------------------

/**
 * Generate ProfilePage schema for the homepage.
 * ProfilePage is the page-type LinkedIn uses for individual profiles; emitting
 * one on the homepage gives Google a direct, page-level entity anchor that
 * competes with LinkedIn for profile-shape queries.
 */
export const getProfilePageSchema = (): object => ({
  '@context': 'https://schema.org',
  '@type': 'ProfilePage',
  '@id': id.profilePage,
  url: CONTACT_INFO.siteUrl,
  name: `${CONTACT_INFO.name} — ${CONTACT_INFO.jobTitle}`,
  description:
    `${CONTACT_INFO.name} is a software engineer based in ${CONTACT_INFO.location}, ` +
    `${CONTACT_INFO.country}, specializing in embedded systems, systems engineering, ` +
    `infrastructure engineering, test-driven development, and agentic AI workflows.`,
  inLanguage: 'en',
  about: { '@id': id.person },
  mainEntity: { '@id': id.person },
  primaryImageOfPage: {
    '@type': 'ImageObject',
    url: `${CONTACT_INFO.siteUrl}/images/werner-bisschoff-software-engineer.webp`,
    width: 1200,
    height: 1200,
  },
  isPartOf: { '@id': id.website },
});

// ---------------------------------------------------------------------------
// WebSite — minimal; SearchAction intentionally omitted
// ---------------------------------------------------------------------------

/**
 * Generate WebSite schema.
 * SearchAction is intentionally omitted: there is no working search endpoint
 * on the site, and a SearchAction whose target 404s produces a worse SERP
 * signal than no SearchAction at all.
 */
export const getWebSiteSchema = (): object => ({
  '@id': id.website,
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  url: CONTACT_INFO.siteUrl,
  name: CONTACT_INFO.name,
  alternateName: 'Werner Bisschoff — Software Engineer',
  description: `${CONTACT_INFO.jobTitle} based in ${CONTACT_INFO.location}, ${CONTACT_INFO.country}`,
  inLanguage: 'en',
  publisher: { '@id': id.person },
  author: { '@id': id.person },
  about: { '@id': id.person },
});

// ---------------------------------------------------------------------------
// FAQPage — references the Person by @id so Google links them
// ---------------------------------------------------------------------------

export const getFaqSchema = (): object => ({
  '@id': id.faqPage,
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  url: `${CONTACT_INFO.siteUrl}/#faq`,
  mainEntity: [
    {
      '@type': 'Question',
      name: `Is ${CONTACT_INFO.name} available for contract or freelance work?`,
      acceptedAnswer: {
        '@type': 'Answer',
        text:
          `Yes — currently open to freelance, contract, part-time, and full-time ` +
          `opportunities. Based in ${CONTACT_INFO.location}, ${CONTACT_INFO.country}, ` +
          `available for remote work internationally. Specializes in embedded systems, ` +
          `systems engineering, infrastructure engineering, test-driven development, ` +
          `and agentic AI workflows.`,
      },
    },
    {
      '@type': 'Question',
      name: `What type of work is ${CONTACT_INFO.name} available for?`,
      acceptedAnswer: {
        '@type': 'Answer',
        text:
          `Open to freelance, contract, part-time, full-time, and remote work ` +
          `opportunities. Based in ${CONTACT_INFO.location}, ${CONTACT_INFO.country}.`,
      },
    },
    {
      '@type': 'Question',
      name: `What are ${CONTACT_INFO.name}'s key skills?`,
      acceptedAnswer: {
        '@type': 'Answer',
        text:
          'Specializes in embedded systems, systems engineering, infrastructure ' +
          'engineering, and spec-driven development with AI-assisted workflows. ' +
          'Practices test-driven development across the stack. Expert in C/C++, Python, ' +
          'JavaScript/TypeScript, Elixir, embedded systems (ESP32, FreeRTOS, BLE), and ' +
          'cloud technologies (AWS, Docker, Pulumi).',
      },
    },
    {
      '@type': 'Question',
      name: `What is ${CONTACT_INFO.name}'s educational background?`,
      acceptedAnswer: {
        '@type': 'Answer',
        text: `${CONTACT_INFO.education.degree} from ${CONTACT_INFO.education.school}, graduated in ${CONTACT_INFO.education.year}.`,
      },
    },
    {
      '@type': 'Question',
      name: `Where is ${CONTACT_INFO.name} located?`,
      acceptedAnswer: {
        '@type': 'Answer',
        text: `Based in ${CONTACT_INFO.location}, ${CONTACT_INFO.country}. Open to remote work internationally.`,
      },
    },
  ],
});

// ---------------------------------------------------------------------------
// ContactPage — references Person and Social profiles
// ---------------------------------------------------------------------------

export const getContactPageSchema = (): object => ({
  '@id': id.contactPage,
  '@context': 'https://schema.org',
  '@type': 'ContactPage',
  url: `${CONTACT_INFO.siteUrl}/contact`,
  name: `Contact ${CONTACT_INFO.name}`,
  description: 'Get in touch to discuss software engineering needs, freelance opportunities, or contract work.',
  about: { '@id': id.person },
  mainEntity: { '@id': id.person },
  contactPoint: {
    '@type': 'ContactPoint',
    email: CONTACT_INFO.email,
    contactType: 'professional',
    availableLanguage: ['English', 'Afrikaans'],
    areaServed: 'Worldwide',
  },
});

// ---------------------------------------------------------------------------
// Knowledge graph — return all entities in one document (homepage)
// ---------------------------------------------------------------------------

/**
 * Return the full identity graph as a single @graph document for the homepage.
 * Use this on the homepage so search engines see a coherent, linked graph
 * instead of scattered, disconnected scripts.
 */
export const getKnowledgeGraph = (): object => ({
  '@context': 'https://schema.org',
  '@graph': [
    getWebSiteSchema(),
    getProfilePageSchema(),
    getPersonSchema(),
    getWorkLocationSchema(),
    getOccupationSchema(),
    getAlumniSchema(),
    getCredentialSchema(),
    getFaqSchema(),
  ],
});

// ---------------------------------------------------------------------------
// Per-experience (JobPosting) and per-post (BlogPosting) — unchanged
// ---------------------------------------------------------------------------

export interface JobPostingInput {
  title: string;
  company: string;
  period: string;
  description: string[];
  location?: string;
  employmentType?: string;
}

/**
 * Generate JobPosting schema for a single experience
 */
export const getJobPostingSchema = (job: JobPostingInput): object => ({
  '@context': 'https://schema.org',
  '@type': 'JobPosting',
  title: job.title,
  employer: {
    '@type': 'Organization',
    name: job.company,
  },
  datePosted: job.period.split('--')[0].trim() + '-01',
  description: job.description.join(' '),
  jobLocation: {
    '@type': 'Place',
    address: {
      '@type': 'PostalAddress',
      addressLocality: job.location || CONTACT_INFO.location,
      addressCountry: CONTACT_INFO.country,
    },
  },
  employmentType: job.employmentType || 'FULL_TIME',
});

export interface BlogPost {
  title: string;
  excerpt?: string;
  publishDate: Date;
  slug: string;
}

/**
 * Generate BlogPosting schema for a blog post.
 * author is referenced by @id so Google links the post to the canonical Person.
 */
export const getBlogPostingSchema = (post: CollectionEntry<'post'>, siteUrl: string): object => {
  const publishDate = post.data.publishDate || new Date();
  const updateDate = post.data.updateDate || post.data.publishDate;
  return {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: post.data.title,
    description: post.data.excerpt || '',
    datePublished: publishDate.toISOString(),
    dateModified: updateDate?.toISOString() || publishDate.toISOString(),
    author: { '@id': id.person },
    publisher: { '@id': id.person },
    mainEntityOfPage: `${siteUrl}/notes/${post.id}`,
    url: `${siteUrl}/notes/${post.id}`,
    image: `${siteUrl}/images/werner-bisschoff-software-engineer.webp`,
    inLanguage: 'en',
  };
};
