import { Sidebar } from "@/components/sidebar";
import { AgentStatusPanel } from "@/components/agent-status-panel";

export default function KnowledgeLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 lg:ml-64 flex min-w-0 overflow-hidden">
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">{children}</div>
        <AgentStatusPanel />
      </main>
    </div>
  );
}
