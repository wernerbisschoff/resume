/**
 * Contact Information Configuration
 *
 * Single source of truth for all contact/personal details across the site.
 * Update these values to change contact information everywhere.
 */

export const CONTACT_INFO = {
  // Personal details
  name: 'Werner Bisschoff',
  jobTitle: 'Software Engineer — Available for Contract',
  location: 'Cape Town',
  country: 'South Africa',

  // Contact
  email: 'contact@bisschoff.dev',
  siteUrl: 'https://werner.bisschoff.dev',

  // Professional focus — used in knowsAbout, hero, llms.txt, footer, OG descriptions
  expertise: [
    'Embedded Systems',
    'Systems Engineering',
    'System Architecture',
    'Infrastructure Engineering',
    'Test-Driven Development',
    'TDD',
    'Agentic Engineering',
    'AI Engineering',
    'AI-Assisted Workflows',
    'Spec-Driven Development',
    'Performance Optimization',
  ],
  // Short-form keywords for places that need compact lists (hero, footers)
  expertiseShort: [
    'Embedded Systems',
    'Systems Engineering',
    'Infrastructure Engineering',
    'Agentic Engineering',
    'TDD',
  ],
  availability: {
    '@type': 'Demand',
    itemOffered: {
      '@type': 'Service',
      name: 'Software Engineering Contract',
      description: 'Freelance software engineer available for contract work, consulting, and part-time engagements.',
    },
  },

  // Resume PDF
  resume: {
    pdfUrl: 'https://github.com/wernerbisschoff/resume/releases/latest/download/W_Bisschoff_CV.pdf',
  },

  // Education
  education: {
    degree: 'B.Eng. Computer and Electronic Engineering',
    field: 'Computer and Electronic Engineering',
    school: 'North-West University',
    year: 2020,
  },

  // Social links
  social: {
    github: {
      url: 'https://github.com/wernerbisschoff',
      username: 'wernerbisschoff',
      icon: 'tabler:brand-github',
    },
    linkedin: {
      url: 'https://linkedin.com/in/wbisschoff',
      username: 'wbisschoff',
      icon: 'tabler:brand-linkedin',
    },
    twitter: {
      url: 'https://twitter.com/wbisschoffdev',
      username: 'wbisschoffdev',
    },
  },
} as const;
