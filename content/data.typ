#let _experience_entries = (
  (
    role: (
      general: "Founder and Host",
      embedded: "Principal Systems Architect",
      enterprise: "Principal Systems Architect",
    ),
    company: "Divergent Tabletop",
    location: "Cape Town",
    start_date: "Jul 2025",
    end_date: none,
    variant_tags: ("general", "embedded", "enterprise"),
    description: (
      general: (
        [Founded neurodivergent-focused peer community; manage event operations and WhatsApp-based community platform.],
        [Applied systems thinking to solve community management challenges through software solutions.],
      ),
      embedded: (
        [Integrated CRDT synchronization layer (y_ex) for real-time modifications; actor-based buffering with sub-50ms sync latency.],
        [Designed dynamic BEAM supervision tree with :one_for_one strategy ensuring 99.9% fault isolation.],
        [Implemented threshold-based buffer flush and heap hibernation (hibernate_after), reducing memory footprint by ~60%.],
      ),
      enterprise: (
        [Implemented PostgreSQL Row-Level Security (RLS) and SET LOCAL transaction-scoped context injection for multi-tenant isolation.],
        [Designed atomic asynchronous flush strategy using in-memory GenServer buffers, reducing database writes by 85%.],
        [Utilized Ecto.Multi atomic chains and Oban transactional workers for safe multi-stage backend edits.],
      ),
    ),
  ),
  (
    role: (
      general: "Full-Stack Software Engineer",
      embedded: "Embedded Systems & Integration Engineer",
      enterprise: "Full-Stack ERPNext & Automation Engineer",
    ),
    company: "FARO Africa",
    location: "Cape Town",
    start_date: "Aug 2024",
    end_date: "Nov 2025",
    variant_tags: ("general", "embedded", "enterprise"),
    description: (
      general: (
        [Extended ERPNext (Python/JS) to improve workflows, pricing logic, and operational reporting (SQL) → reduced manual reporting time.],
        [Built Expo mobile app with NFC (ISO 14443-4 APDUs) for e-paper price tags → enabled real-time price updates.],
        [Provisioned AWS infrastructure with Pulumi; deployed Inngest and PayloadCMS services.],
        [Introduced LLM-assisted development workflows → improved debugging speed and code review throughput.],
      ),
      embedded: (
        [Designed ISO 14443-4 NFC communication architectures for e-paper display nodes and card reader matrices.],
        [Built Python-based hardware peripheral simulators to catch edge-case device state corruptions prior to flashing.],
        [Introduced LLM-assisted development workflows to improve debugging speed and code review throughput.],
      ),
      enterprise: (
        [Refactored and extended ERPNext via Python and JavaScript server hooks, optimizing pricing matrices and BI reporting.],
        [Architected migration of internal Retool workflows to Expo/React Native, reducing vendor licensing overhead.],
        [Built custom NFC scanner utilities within Expo for instantaneous physical inventory syncs.],
        [Provisioned AWS infrastructure with Pulumi, deploying Inngest event-driven functions and PayloadCMS.],
      ),
    ),
  ),
  (
    role: (
      general: "Embedded Software Engineer",
      embedded: "Firmware Engineer (Contract)",
      enterprise: "Enterprise Infrastructure & Tooling Engineer",
    ),
    company: "Ingenics Digital GmbH (through ViVa Outsourcing)",
    location: "Remote",
    start_date: "Mar 2023",
    end_date: "May 2024",
    variant_tags: ("general", "embedded", "enterprise"),
    description: (
      general: (
        [Designed event-driven FSM for I2C-based embedded system (C++/FreeRTOS) → maintainable architecture, fewer bugs.],
        [Developed ESP32 applications (C/C++, ESP-IDF) with configurable BLE stack and FOTA updates.],
        [Built Python tooling for serial/BLE communication and hardware mocks → accelerated testing workflows.],
      ),
      embedded: (
        [Architected deterministic FSMs on dual-core ESP32 using FreeRTOS for concurrent sensor arrays.],
        [Developed Cap'n Proto IPC over serial lines, achieving sub-millisecond serialization latency.],
      ),
      enterprise: (
        [Built modular Python utilities and automation scripts for internal configuration schema validation.],
        [Designed data handling pipelines ensuring transfer consistency across runtime platforms.],
        [Developed Python hardware mocks enabling faster development cycles with fewer hardware dependencies.],
      ),
    ),
  ),
  (
    role: (
      general: "Software Developer",
      embedded: "Software Developer",
    ),
    company: "UMAN Technologies",
    location: "Cape Town",
    start_date: "Mar 2021",
    end_date: "Dec 2022",
    variant_tags: ("general", "embedded"),
    description: (
      general: (
        [Implemented SOME/IP RPC services; optimized performance bottlenecks with perf.],
        [Built IPC/RPC layers (C++/Python) using Cap'n Proto; led small team using AGILE practices.],
      ),
      embedded: (
        [Implemented RPC services using SOME/IP protocol; reduced bottlenecks with perf.],
        [Built IPC/RPC layers in C++ and Python using Cap'n Proto; designed node trees for IPC interface.],
      ),
    ),
  ),
  (
    role: (
      general: "Junior Lecturer",
      embedded: "Junior Lecturer",
      enterprise: "Junior Lecturer",
    ),
    company: "North-West University",
    location: "Potchefstroom",
    start_date: "Feb 2020",
    end_date: "Dec 2020",
    variant_tags: ("general", "embedded", "enterprise"),
    description: (
      general: (
        [Lectured Python and C++ programming for first-year IT students (remote and in-person).],
      ),
      embedded: (
        [Lectured Python and C++ programming for first-year IT students.],
      ),
      enterprise: (
        [Lectured Python and C++ programming for first-year IT students.],
      ),
    ),
  ),
)

#let _education_entries = (
  (
    degree: "B.Eng. Computer and Electronic Engineering",
    institution: "North-West University",
    location: "Potchefstroom",
    graduation_year: "2020",
    details: (
      general: (
        [Focus on embedded systems, software engineering, and electronic design],
        [NFC payment emulator (Kotlin/Android), STM32 firmware (C), PID motor controller (Arduino)],
        [Data analysis with Python/Pandas using linear regression, correlation and machine learning],
      ),
      embedded: (
        [Focus on embedded systems, software engineering, and electronic design],
        [Developed NFC payment protocol emulator (Kotlin/Android), STM32 firmware (C), PID motor controller (Arduino)],
      ),
      enterprise: (
        [Focus on embedded systems, software engineering, and electronic design],
        [Developed data analysis pipeline with Python/Pandas (linear regression, ML); built NFC payment emulator (Kotlin/Android)],
      ),
    ),
  ),
)

#let _skill_categories = (
  (category_name: "Primary", skills: ("C/C++", "Python", "FreeRTOS", "ESP32/ESP-IDF", "NFC APDU (ISO 14443-4)"), variant: "general"),
  (category_name: "Secondary", skills: ("NimBLE", "UART/SPI/I2C", "TinyFrame", "BLE", "Hardware-in-the-Loop Testing"), variant: "general"),
  (category_name: "Foundational", skills: ("SQL", "Docker", "CI/CD", "Git", "Linux"), variant: "general"),
  (category_name: "Other", skills: ("React", "Phoenix", "AWS", "Pulumi", "ERPNext"), variant: "general"),
  (category_name: "Primary", skills: ("C++", "FreeRTOS", "ESP32/ESP-IDF", "NFC APDU (ISO 14443-4)"), variant: "embedded"),
  (category_name: "Secondary", skills: ("NimBLE", "UART/SPI/I2C", "TinyFrame", "Hardware-in-the-Loop (HIL) Testing"), variant: "embedded"),
  (category_name: "Foundational", skills: ("Assembly", "Digital Logic", "System Modeling"), variant: "embedded"),
  (category_name: "Other", skills: ("ERPNext (Integration-focused)", "Expo Mobile"), variant: "embedded"),
  (category_name: "Primary", skills: ("Python", "ERPNext/Frappe Framework", "Expo (React Native)", "Inngest"), variant: "enterprise"),
  (category_name: "Secondary", skills: ("AWS", "Pulumi (IaC)", "PostgreSQL (RLS)", "Docker"), variant: "enterprise"),
  (category_name: "Foundational", skills: ("SQL", "Object-Oriented Design", "Spec-Driven Development"), variant: "enterprise"),
  (category_name: "Other", skills: ("C++", "FreeRTOS (Low-level integration support)"), variant: "enterprise"),
)

#let _project_entries = (
  (
    name: "Divergent Tabletop Wiki",
    description: (
      general: ([Built a community wiki using Astro, Elixir, and Docker for knowledge management], [Documented event frameworks, onboarding processes, and communication best practices], [Created tooling for content management and community operations]),
    ),
    link: none,
    variant_tags: ("general", "embedded", "enterprise"),
  ),
  (
    name: "Ingenics Digital GmbH \u{2014} Event-Driven FSM for Embedded Systems",
    description: (
      general: ([Designed event-driven finite state machine for I2C-based embedded system using C++ and FreeRTOS], [Solved complex state management challenges in real-time embedded environment], [Outcome: Maintainable in-house architecture leading to fewer bugs and quicker development cycles]),
    ),
    link: none,
    variant_tags: ("general", "embedded"),
  ),
)

#let _cover_letter_data = (
  recipient_name: none,
  recipient_title: none,
  company: none,
  date: none,
  about_me: (
    general: [
      I am a software engineer with over 5 years of experience bridging hardware, full-stack development, and resilient system architecture. My approach combines deep technical expertise with a rigorous, AI-augmented methodology\u{2014}utilizing agentic workflows to ship reliable software at high velocity. With a background in Computer and Electronic Engineering (B.Eng.), I don't just write code; I design systems that last, from low-level firmware to cloud-native infrastructures.
    ],
    embedded: [
      I am writing to express my interest in the Senior Systems Engineering position at [Company]. I specialize in engineering deterministic, real-time software architectures (C/C++, FreeRTOS, Elixir/OTP) and secure, spec-driven communication protocols. Throughout my career, my focus has been on eliminating runtime faults and managing high-concurrency systems at the edge and data boundaries.
    ],
    enterprise: [
      I am writing to explore the Enterprise Systems Architect position at [Company]. I bring over 5 years of experience designing robust business automation engines, multi-tenant database infrastructures, and scalable custom extensions within the ERPNext/Frappe ecosystem.
    ],
  ),
  why_me: (
    general: (
      [
        Hard Engineering & System Design: My foundations are in complex, real-time systems. At Ingenics Digital, I designed an event-driven finite state machine for embedded systems using C++ and FreeRTOS, creating a maintainable architecture that reduced bugs and accelerated development cycles. Whether I am working with memory-constrained microcontrollers or distributed cloud services, I prioritize long-term maintainability and architectural integrity.
      ],
      [
        Strategic AI Integration: I treat AI as a powerful force multiplier for my existing engineering skills, applying it where it offers the greatest leverage while remaining fully capable of developing complex systems manually. I use Claude Code for surgical, interactive debugging and Droid by Factory for programmatic automation. This allows me to maintain high code quality and rigour while moving at the pace of a modern, high-impact environment, without incurring technical debt.
      ],
      [
        Full-Stack Versatility & Impact: My technical breadth is grounded in practical delivery. At FARO Africa, I extended ERPNext systems (Python/JS), built mobile features in Expo with NFC integration, and provisioned AWS infrastructure with Pulumi. This versatility is complemented by my "impact over process" philosophy\u{2014}demonstrated by my work founding Divergent Tabletop, where I apply systems thinking to solve real-world community challenges.
      ],
      [
        Resilient Infrastructure: Beyond application code, I am comfortable with the "plumbing" of modern software, including Docker for development and CI/CD. I am currently preparing to open-source my community wiki project, reflecting my commitment to shared knowledge and the Open Source ecosystem.
      ],
    ),
    embedded: (
      [
        Recently, as Principal Systems Architect for the open-source Divergent Tabletop ecosystem, I engineered a high-concurrency real-time wiki engine using Elixir with the y_ex CRDT library. By implementing a dynamic supervision tree and an actor-based memory buffering architecture, I achieved 99.9% fault isolation and reduced per-session memory overhead by 60%.
      ],
    ),
    enterprise: (
      [
        My recent work highlights my ability to transform complex real-world operational challenges into scalable, secure software architectures. As the Principal Systems Architect for the Divergent Tabletop documentation engine, I designed and deployed a single-database multi-tenant architecture utilizing PostgreSQL Row-Level Security (RLS) and transaction-scoped context injection. This strategy, combined with an in-memory transactional flushing architecture, safely reduced database write volumes by 85% under heavy user concurrency. Additionally, my background at FARO Africa includes leading the migration of business workflows from Retool into custom Expo mobile environments, significantly lowering operational latency and eliminating third-party licensing dependencies.
      ],
    ),
  ),
  how_i_work: (
    embedded: [
      I approach software through the lens of Spec-Driven Development (SDD) to ensure code correctness and maintain clear, robust architectures. I am looking forward to bringing this systems-level discipline to [Company]'s engineering team.
    ],
    enterprise: [
      I execute tasks using strict Spec-Driven Development frameworks to deliver highly maintainable codebases that align perfectly with business goals. I am eager to help optimize and scale [Company]'s enterprise core.
    ],
  ),
)

#let cv_data = (
  name: "Werner Bisschoff",
  email: "werner@bisschoff.dev",
  phone: "071 826 2066",
  location: "Cape Town, Western Cape, South Africa",
  position: (
    general: "Software Engineer",
    embedded: "Embedded Systems & Real-Time Software Engineer",
    enterprise: "Enterprise Systems & Automation Architect",
  ),

  summary: (
    general: [
      Software engineer with 5+ years of experience bridging hardware and full-stack development. I combine technical depth in C++ and Python with a rigorous, agentic engineering methodology. My focus is on resilient system design and productivity-enhancing AI workflows, governed by security, processes, and specification-driven development.
    ],
    embedded: [
      Rigorous Systems Engineer with 5+ years of experience engineering real-time, event-driven software architectures (C/C++, FreeRTOS) and secure, deterministic communication protocols. Specializes in designing robust firmware, high-performance IPC mechanisms, and hardware-in-the-loop simulation frameworks. Governed by strict Spec-Driven Development (SDD) methodologies and automated validation pipelines to eliminate runtime faults in production environments.
    ],
    enterprise: [
      Strategic Enterprise Software Architect with 5+ years of experience engineering robust business automation platforms, custom ERP extensions, and scalable API layers. Expert in the Frappe/ERPNext ecosystem, asynchronous workflow systems, and cross-platform mobile application deployment (Expo/React Native). Proven track record of translating complex real-world operations into scalable, type-safe data schemas governed by strict Spec-Driven Development (SDD) paradigms.
    ],
  ),

  ai_policy: (
    [I treat AI as an agentic partner within a strict engineering framework, moving beyond "vibe-coding" to structured, audit-ready workflows:],
    [Spec-Driven Development (SDD): Prioritize context-heavy specifications to ensure alignment; AI-generated outputs are treated as hypotheses validated by human-led TDD.],
    [Data Security: Enforce mandatory sandboxing for all agentic projects; strictly prohibit credential access and utilize tool-based retrieval for scoped, anonymized data only.],
    [Engineering Rigour: All AI-assisted output undergoes rigorous human-in-the-loop review to ensure it meets enterprise quality and compliance benchmarks.],
    [Privacy by Design: AI workflows are architected to avoid direct database access; sensitive data remains behind scoped, tool-mediated retrieval with no standing credentials exposed to agents.],
  ),

  job_target: [
    Seeking a mid to senior software engineering role (remote preferred, hybrid max. 2 days/week on-site in Cape Town) with emphasis on embedded systems, backend services, or AI-assisted development workflows. Prefers small, focused teams with clear goals and engineering culture. Open to permanent or contract (3+ months) arrangements.
  ],

  experience: _experience_entries,
  education: _education_entries,
  skills: _skill_categories,
  cover_letter_data: _cover_letter_data,
)
