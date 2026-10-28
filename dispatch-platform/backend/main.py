from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from backend.config import settings
from backend.auth import get_current_user, supabase
from backend.agents.triage_agent import TriageAgent
from backend.agents.hamiltonian_agent import HamiltonianAgent
from backend.agents.solution_agent import SolutionAgent
from backend.solvers.cloud_runner import run_cloud_qaoa

app = FastAPI(title="Quantum Dispatch Gateway")

nebius_client = OpenAI(
    api_key=settings.NEBIUS_API_KEY,
    base_url=settings.NEBIUS_BASE_URL
)

triage_agent = TriageAgent(nebius_client)
hamiltonian_agent = HamiltonianAgent(nebius_client)
solution_agent = SolutionAgent(nebius_client)

class CreateDispatchRequest(BaseModel):
    title: str
    manifest_text: str
    compute_target: str  # "LOCAL_GPU" or "NEBIUS_CLOUD"

class CompleteLocalRequest(BaseModel):
    bitstring: str
    solver_latency_ms: int
    energy: float

@app.post("/api/v1/dispatch/create")
async def create_dispatch(req: CreateDispatchRequest, user_id: str = Depends(get_current_user)):
    insert_res = supabase.table("dispatch_runs").insert({
        "user_id": user_id,
        "title": req.title,
        "status": "RUNNING",
        "compute_target": req.compute_target,
        "raw_payload": {"manifest": req.manifest_text}
    }).execute()
    run_id = insert_res.data[0]["id"]

    try:
        graph_dict, nano_triage_ms = triage_agent.process(req.manifest_text)
        hamiltonian_spec, ultra_ms = hamiltonian_agent.process(graph_dict)

        supabase.table("dispatch_runs").update({
            "graph_data": graph_dict,
            "hamiltonian_spec": hamiltonian_spec,
            "telemetry": {
                "triage_ms": nano_triage_ms,
                "hamiltonian_ms": ultra_ms
            }
        }).eq("id", run_id).execute()

        if req.compute_target == "LOCAL_GPU":
            return {
                "run_id": run_id,
                "status": "DELEGATE_LOCAL",
                "graph_data": graph_dict,
                "hamiltonian_spec": hamiltonian_spec,
                "telemetry": {
                    "triage_ms": nano_triage_ms,
                    "hamiltonian_ms": ultra_ms
                }
            }
        else:
            solver_res, solver_ms = run_cloud_qaoa(graph_dict, hamiltonian_spec)
            bitstring = solver_res["best_bitstring"]
            solution_data, decode_ms = solution_agent.process(graph_dict, bitstring)

            total_telemetry = {
                "triage_ms": nano_triage_ms,
                "hamiltonian_ms": ultra_ms,
                "solver_ms": solver_ms,
                "decode_ms": decode_ms,
                "energy": solver_res.get("energy", 0.0)
            }

            supabase.table("dispatch_runs").update({
                "status": "COMPLETED",
                "optimal_bitstring": bitstring,
                "solution_json": solution_data,
                "telemetry": total_telemetry
            }).eq("id", run_id).execute()

            return {
                "run_id": run_id,
                "status": "COMPLETED",
                "bitstring": bitstring,
                "solution": solution_data,
                "telemetry": total_telemetry
            }
    except Exception as e:
        supabase.table("dispatch_runs").update({
            "status": "FAILED",
            "telemetry": {"error": str(e)}
        }).eq("id", run_id).execute()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/dispatch/{run_id}/complete_local")
async def complete_local(run_id: str, req: CompleteLocalRequest, user_id: str = Depends(get_current_user)):
    run_res = supabase.table("dispatch_runs").select("*").eq("id", run_id).eq("user_id", user_id).execute()
    if not run_res.data:
        raise HTTPException(status_code=404, detail="Run not found")
    
    run_record = run_res.data[0]
    graph_dict = run_record["graph_data"]
    solution_data, decode_ms = solution_agent.process(graph_dict, req.bitstring)

    existing_telemetry = run_record.get("telemetry") or {}
    existing_telemetry["solver_ms"] = req.solver_latency_ms
    existing_telemetry["decode_ms"] = decode_ms
    existing_telemetry["energy"] = req.energy

    supabase.table("dispatch_runs").update({
        "status": "COMPLETED",
        "optimal_bitstring": req.bitstring,
        "solution_json": solution_data,
        "telemetry": existing_telemetry
    }).eq("id", run_id).execute()

    return {"status": "SUCCESS", "solution": solution_data, "telemetry": existing_telemetry}