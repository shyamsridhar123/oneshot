"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

const footerLinks = {
  platform: [
    { label: "Agents", href: "#agents" },
    { label: "Capabilities", href: "#capabilities" },
    { label: "Roadmap", href: "#implementation" },
  ],
  demos: [
    { label: "Chat Interface", href: "/chat" },
    { label: "Research", href: "/research" },
    { label: "Proposals", href: "/proposals" },
    { label: "Knowledge", href: "/knowledge" },
  ],
};

export function FooterSection() {
  return (
    <footer className="bg-card border-t border-border">
      {/* CTA Section */}
      <div className="py-24 bg-gradient-to-br from-primary/5 via-background to-chart-2/5">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl md:text-5xl font-bold mb-6">
              We&apos;re not building IT infrastructure.
              <br />
              <span className="text-primary">We&apos;re building core IP amplification.</span>
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
              OneShot represents our commitment to making every content creator&apos;s expertise 
              instantly amplified by the collective intelligence of the entire team.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button size="lg" className="text-lg px-8 py-6" asChild>
                <Link href="/chat">
                  Start Using OneShot
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Links */}
      <div className="py-16 border-t border-border">
        <div className="container mx-auto px-6">
          <div className="max-w-6xl mx-auto">
            <div className="grid md:grid-cols-3 gap-12">
              {/* Brand */}
              <div className="md:col-span-1">
                <Link href="/" className="inline-flex items-center gap-2 mb-4">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-chart-2 flex items-center justify-center">
                    <span className="text-white font-bold text-lg">O</span>
                  </div>
                  <span className="text-xl font-bold">OneShot</span>
                </Link>
                <p className="text-sm text-muted-foreground mb-4">
                  Multi-agent AI platform for social media content creation, powered by Microsoft Agent Framework.
                </p>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  Demo environment
                </div>
              </div>

              {/* Platform Links */}
              <div>
                <h4 className="font-semibold mb-4">Platform</h4>
                <ul className="space-y-3">
                  {footerLinks.platform.map((link, i) => (
                    <li key={i}>
                      <Link 
                        href={link.href} 
                        className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                      >
                        {link.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Demo Links */}
              <div>
                <h4 className="font-semibold mb-4">Try It</h4>
                <ul className="space-y-3">
                  {footerLinks.demos.map((link, i) => (
                    <li key={i}>
                      <Link 
                        href={link.href} 
                        className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                      >
                        {link.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Bottom bar */}
            <div className="mt-16 pt-8 border-t border-border flex flex-col md:flex-row items-center justify-between gap-4">
              <p className="text-sm text-muted-foreground">
                © {new Date().getFullYear()} OneShot by NotContosso Inc. Built with Microsoft Agent Framework.
              </p>
              <p className="text-sm text-muted-foreground">
                Proof of Concept · Not for Production Use
              </p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
