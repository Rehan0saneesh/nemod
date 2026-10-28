'use client';
import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import Link from 'next/navigation';

export default function DashboardPage() {
  const [runs, setRuns] = useState<any[]>([]);

  useEffect(() => {
    async function loadRuns() {
      const { data } = await supabase
        .from('dispatch_runs')
        .select('*')
        .order('created_at', { ascending: false });
      if (data) setRuns(data);
    }
    loadRuns();
  }, []);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Dispatch History & Active Runs</h1>
      <div className="bg-slate-900 rounded border border-slate-800 overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-slate-800 text-slate-400">
            <tr>
              <th className="p-3">Title</th>
              <th className="p-3">Target</th>
              <th className="p-3">Status</th>
              <th className="p-3">Optimal Bitstring</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((r) => (
              <tr key={r.id} className="border-t border-slate-800">
                <td className="p-3 font-medium">{r.title}</td>
                <td className="p-3">{r.compute_target}</td>
                <td className="p-3">
                  <span className={`px-2 py-1 rounded text-xs ${
                    r.status === 'COMPLETED' ? 'bg-emerald-900 text-emerald-300' : 'bg-amber-900 text-amber-300'
                  }`}>
                    {r.status}
                  </span>
                </td>
                <td className="p-3 font-mono">{r.optimal_bitstring || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}