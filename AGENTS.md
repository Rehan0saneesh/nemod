# TASK: Build the Full-Stack Quantum-Classical Fleet Dispatch Platform

You are an expert autonomous software engineer. Construct the entire production repository for the **Quantum-Classical Fleet Dispatch Platform** from scratch. 

The application solves $NP$-hard logistics dispatch bottlenecks using a hybrid architecture:
1. **Tiered Reasoning:** NVIDIA Nemotron models hosted on Nebius Token Factory handle natural language ingestion, QUBO Hamiltonian compilation, and bitstring solution decoding.
2. **GPU Optimization Kernel:** NVIDIA CUDA-Q simulates the parameterized QAOA state vector (either on local NVIDIA hardware or remote GPU container).
3. **Multi-Platform Access:** A native C++20 Qt6 desktop client (supporting local GPU or cloud dispatch) and a Next.js 14 Web client (pure cloud dispatch).
4. **Cloud Persistence:** Managed Supabase PostgreSQL with Row-Level Security (RLS) keeping records synchronized across devices under user accounts.

Generate every single file, build configuration, script, schema, and interface with full implementations (no placeholders, no omitted TODOs).

---

## 1. Directory Structure to Create

```text
.
├── .env.example
├── CMakeLists.txt                         # Top-level build definition for C++ Qt6 GUI
├── database/
│   └── migrations.sql                     # Supabase schema, RLS, and indexes
├── docker/
│   ├── Dockerfile.cloud-worker            # Nebius Serverless Job container with CUDA-Q
│   └── Dockerfile.gateway                 # FastAPI Gateway container for Nebius Endpoints
├── backend/
│   ├── requirements.txt
│   ├── main.py                            # FastAPI Gateway with Supabase Auth
│   ├── config.py                          # Environment variable parser
│   ├── auth.py                            # Supabase JWT validator dependency
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── triage_agent.py                # Nemotron-Nano: schema extraction & graph parsing
│   │   ├── hamiltonian_agent.py           # Nemotron-3 Ultra: QUBO math formulation & prior angles
│   │   └── solution_agent.py              # Nemotron-Nano: bitstring to route mapping
│   ├── solvers/
│   │   ├── __init__.py
│   │   ├── base.py                        # Abstract solver interface
│   │   ├── local_cudaq.py                 # Local NVIDIA GPU simulator via cudaq
│   │   └── cloud_runner.py                # Remote worker dispatcher
│   └── worker.py                          # Entrypoint script inside Dockerfile.cloud-worker
├── gui/                                   # Native C++20 / Qt6 Desktop Client
│   ├── include/
│   │   ├── main_window.hpp                # Main dashboard with controls, logs, metrics
│   │   ├── auth_dialog.hpp                # Supabase Login / Register modal
│   │   ├── cloud_sync.hpp                 # REST network manager communicating with backend
│   │   └── local_runner.hpp               # Subprocess caller for local CUDA-Q Python execution
│   └── src/
│       ├── main.cpp                       # App entrypoint & theme initialization
│       ├── main_window.cpp                # Layout, splitters, execution flow, charts
│       ├── auth_dialog.cpp                # Session storage & JWT retrieval
│       ├── cloud_sync.cpp                 # Async QNetworkAccessManager implementation
│       └── local_runner.cpp               # Spawns local solver script and pipes JSON stdout
└── web/                                   # Next.js 14 App Router Web Client
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.js
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx                       # Landing / redirect
    │   ├── (auth)/login/page.tsx          # Supabase email/password login
    │   ├── dashboard/page.tsx             # Run history, metrics waterfall, launcher
    │   └── dispatch/[id]/page.tsx         # Live run detail view & Leaflet route display
    ├── components/
    │   ├── Navbar.tsx
    │   ├── RouteMap.tsx                   # Interactive map rendering nodes & solved paths
    │   └── MetricsPanel.tsx               # Latency breakdown (Nano vs Ultra vs CUDA-Q)
    └── lib/
        └── supabase.ts                    # Supabase browser client initialization