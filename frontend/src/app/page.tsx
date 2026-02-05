import {
  HeroSection,
  ParadigmShiftSection,
  AgentsSection,
  CapabilitiesSection,
  RoadmapSection,
  FooterSection,
  LandingNav,
} from "@/components/landing";

export default function Home() {
  return (
    <div className="min-h-screen">
      <LandingNav />
      <HeroSection />
      <ParadigmShiftSection />
      <AgentsSection />
      <CapabilitiesSection />
      <RoadmapSection />
      <FooterSection />
    </div>
  );
}
