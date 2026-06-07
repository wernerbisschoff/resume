# Experience Master — Werner Bisschoff

This is the canonical source of truth for all employment experience, extracted from the
original LaTeX awesome-cv templates (commit `4020c57`). Each CV variant
(general / embedded / enterprise) curates from this document.

---

## 1. Divergent Tabletop | Cape Town, ZA

### General / Embedded / Enterprise
- **Role (general):** Founder and Host
- **Role (embedded):** Principal Systems Architect
- **Role (enterprise):** Principal Systems Architect
- **Dates:** Jul 2025 – Present

#### General bullets
- Founded neurodivergent-focused peer community; manage event operations and WhatsApp-based community platform.
- Applied systems thinking to solve community management challenges through software solutions.

#### Embedded bullets
- Engineered and deployed a distributed knowledge-management infrastructure
- Integrated a CRDT synchronization layer (`y_ex`) to handle real-time modifications; implemented an actor-based buffering model that reduced state-sync latency to sub-50ms thresholds.
- Designed a dynamic BEAM supervision tree with a `:one_for_one` strategy to isolate concurrent page editing instances, ensuring 99.9% fault isolation and zero system-wide cascading crashes.
- Implemented a threshold-based buffer flush and scheduled heap hibernation (`hibernate_after`), reducing process memory footprints by ~60% under active network I/O concurrency.
- Applied Monotropic focus principles and Universal Design to minimize user information processing overhead and ensure highly predictable, deterministic information layout.

#### Enterprise bullets
- Engineered and hosted an enterprise-grade documentation ecosystem
- Implemented a single-database multi-tenant separation engine using PostgreSQL Row-Level Security (RLS) and transaction-scoped local parameters (`SET LOCAL`), enforcing strict data silos across isolated groups.
- Designed an atomic asynchronous flush strategy using in-memory GenServer storage buffers, reducing database persistent write transactions by 85% during periods of high user interaction.
- Utilized `Ecto.Multi` atomic chains and `Oban` transactional background workers to ensure multi-stage backend edits (e.g., structural document renaming and incoming backlink indexing) execute completely or roll back safely.
- Applied Universal Design and Executive Functioning support models to product UX/UI; established highly structured, low-context asynchronous operational playbooks that minimized cognitive friction for contributors.

---

## 2. FARO Africa | Cape Town, ZA

- **Role (general):** Full-Stack Software Engineer
- **Role (embedded):** Embedded Systems & Integration Engineer
- **Role (enterprise):** Full-Stack ERPNext & Automation Engineer
- **Dates:** Aug 2024 – Nov 2025

#### General bullets
- Extended ERPNext using Python/JavaScript to improve workflows, pricing logic, and operational reporting (SQL) → reduced manual reporting time and improved data accuracy
- Built mobile application in Expo, including NFC (ISO 14443-4 APDUs) for e-paper price tags and card operations → enabled real-time price updates with fewer tagging errors
- Migrated internal mobile Retool workflows to Expo → improved performance and enhanced long-term maintainability
- Developed and maintained C# APIs supporting internal systems.
- Provisioned AWS infra with Pulumi and deployed services including Inngest and PayloadCMS.
- Diagnosed and resolved issues in a large existing ERPNext installation.
- Introduced LLM-assisted development workflows → improved debugging speed and code review throughput, enabling faster iteration

#### Embedded bullets
- Designed ISO 14443-4 NFC communication architectures for e-paper display nodes and secure card reader matrices.
- Engineered lock-free asynchronous device management services bridging hardware peripherals with application layers.
- Built Python-based hardware peripheral simulators to catch edge-case device state corruptions prior to flashing.
- Introduced LLM-assisted development workflows to improve debugging speed and code review throughput.

#### Enterprise bullets
- Refactored and extended ERPNext via Python and JavaScript server hooks, optimizing pricing matrices and business intelligence reporting.
- Architected migration of internal Retool workflows to React Native/Expo mobile ecosystem, reducing vendor licensing overhead.
- Built custom NFC scanner communication utilities within Expo applications for instantaneous physical inventory syncs.
- Provisioned AWS infrastructure with Pulumi, deploying Inngest event-driven functions and PayloadCMS.
- Diagnosed and resolved issues in a large existing ERPNext installation; introduced LLM-assisted debugging workflows.

---

## 3. Ingenics Digital GmbH | Remote / Germany

- **Role (general):** Embedded Software Engineer
- **Role (embedded):** Firmware Engineer (Contract)
- **Role (enterprise):** Enterprise Infrastructure & Tooling Engineer
- **Dates:** Mar 2023 – May 2024

#### General bullets
- Designed an event-driven finite state machine for an I2C-based embedded system using C++ and FreeRTOS → created maintainable in-house architecture leading to fewer bugs and quicker development
- Developed ESP32 applications using C/C++ and ESP-IDF
- Integrated a configurable low-energy BLE stack for device communication
- Built Python-based tooling for serial/BLE communication, including client-facing test executables → accelerated testing and debugging workflows
- Created Python hardware mocks for rapid iteration and early-stage testing → enabled faster development cycles with fewer hardware dependencies
- Managed fast, reliable data interchange using a compact TinyFrame binary protocol
- Implemented asynchronous communication workflows with Python and Pytest
- Developed an active object within the QP Real-Time Embedded Framework (with QSPY) to simulate device behaviour
- Integrated a configurable BLE stack for device communication and implemented FOTA firmware updates over BLE

#### Embedded bullets
- Architected deterministic finite state machines (FSM) on dual-core ESP32 using FreeRTOS for concurrent sensor arrays.
- Developed Cap'n Proto inter-process communication over serial lines, achieving sub-millisecond serialization latency.
- Implemented strict compile-time and runtime hardware state guards via rigorous assertions preventing fragmentation.

#### Enterprise bullets
- Built modular Python utility structures and automation scripts for internal configuration schema validation.
- Designed data handling pipelines ensuring data transfer consistency across runtime platforms using declarative specifications.
- Developed Python hardware mocks enabling faster development cycles with fewer hardware dependencies.

---

## 4. UMAN Technologies | Century City, Cape Town

- **Role (general):** Software Developer
- **Role (embedded):** Software Developer
- **Role (enterprise):** (not used)
- **Dates:** Mar 2021 – Dec 2022

#### General bullets
- Creating and maintaining Docker containers for development and CI/CD testing → improved development environment consistency
- Implementing and testing new services using RPC based on the SOME/IP protocol, as well as using perf to reduce performance bottlenecks
- Implementing IPC/RPC in existing C++ programs and Python scripts using Cap'n Proto and pycapnp
- Implementing a node tree to expose process-related variables and function calls to the IPC interface
- Analysing TCP/UDP traffic with Wireshark
- Leading a small team using AGILE development practices, including onboarding and mentoring new software developers

#### Embedded bullets
- Implemented RPC services using SOME/IP protocol and reduced performance bottlenecks with perf.
- Built IPC/RPC layers in C++ and Python using Cap'n Proto; designed node trees exposing process variables via IPC interface.

---

## 5. North-West University | Potchefstroom

- **Role (general):** Junior Lecturer
- **Role (embedded):** Junior Lecturer
- **Role (enterprise):** Junior Lecturer
- **Dates:** Feb 2020 – Dec 2020

#### General / Embedded / Enterprise
- Lectured Python and C++ programming for Introduction to Programming for first year IT students in both remote and in-person settings

---

## Education

**B.Eng. Computer and Electronic Engineering** | North-West University | Potchefstroom | 2020

#### General
- Focus on embedded systems, software engineering, and electronic design
- Developing an Android app with Kotlin to emulate an ISO 14443 protocol-based NFC payment system
- Developing microcontroller logic with C and the STM32 system as well as utilizing STM32CubeMX
- Implementing a PID controller with an Arduino to control a DC motor's voltage and speed
- Cleaning and analysing data from large spreadsheets with Python and Pandas, utilizing linear regression, correlation and machine learning

#### Embedded
- Focus on embedded systems, software engineering, and electronic design
- Developed NFC payment protocol emulator (Kotlin/Android), STM32 firmware (C), and PID motor controller (Arduino)

#### Enterprise
- Focus on embedded systems, software engineering, and electronic design
- Developed data analysis pipeline with Python/Pandas (linear regression, ML); built NFC payment emulator (Kotlin/Android)

---

## Skills

### General
- **Systems Architecture:** Event-driven FSM | RPC/IPC (Cap'n Proto, SOME/IP) | State machines | Node trees
- **Testing & Quality:** Unit testing (Pytest) | Hardware mocks | Test executables | Code coverage analysis
- **Development Infrastructure:** Docker | CI/CD | Cloudflare | Terraform | Linux | WSL2
- **Agentic Engineering & AI Integration:** Agentic workflows | Claude Code | Spec-Driven TDD | Prompt Engineering
- **Workflow Automation:** ERPNext | Python tooling | Retool → Expo migration
- **Languages:** C/C++ | Python | JavaScript/TypeScript | SQL | Elixir
- **Embedded Systems:** ESP32/ESP-IDF | FreeRTOS | NimBLE | QP RTOS | TinyFrame protocol
- **Web Development:** ReactJS | AstroJS | Django REST API | TailwindCSS | Phoenix

### Embedded
- **Primary:** C++ | FreeRTOS | ESP32/ESP-IDF | NFC APDU (ISO 14443-4)
- **Secondary:** NimBLE | UART/SPI/I2C | TinyFrame | Hardware-in-the-Loop (HIL) Testing
- **Foundational:** Assembly | Digital Logic | System Modeling
- **Other:** ERPNext (Integration-focused) | Expo Mobile

### Enterprise
- **Primary:** Python | ERPNext/Frappe Framework | Expo (React Native) | Inngest
- **Secondary:** AWS | Pulumi (IaC) | PostgreSQL (RLS) | Docker
- **Foundational:** SQL | Object-Oriented Design | Spec-Driven Development
- **Other:** C++ | FreeRTOS (Low-level integration support)

---

## Projects

### Divergent Tabletop Wiki | Community Knowledge Base | Jun 2025 – Present
- Built a community wiki using Astro, Elixir, and Docker for knowledge management
- Documented event frameworks, onboarding processes, and communication best practices
- Created tooling for content management and community operations

### Ingenics Digital GmbH | Event-Driven FSM for Embedded Systems | Mar 2023 – May 2024
- Designed event-driven finite state machine for I2C-based embedded system using C++ and FreeRTOS
- Solved complex state management challenges in real-time embedded environment
- **Outcome:** Maintainable in-house architecture leading to fewer bugs and quicker development cycles
