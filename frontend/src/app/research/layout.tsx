import { Sidebar } from "@/components/sidebar";
import { AgentStatusPanel } from "@/components/agent-status-panel";

export default function ResearchLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 lg:ml-64 xl:mr-72 flex">
        <div className="flex-1 flex flex-col">{children}</div>
        <AgentStatusPanel />
      </main>
    </div>
  );
}
