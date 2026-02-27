#!/usr/bin/env python3
"""
ui-ux-pro-max design intelligence search script.

This script queries the design pattern database used by the ui-ux-pro-max skill.
It supports domain-specific searches, design system generation, and stack guidelines.

INSTALLATION NOTE:
  This script requires the ui-ux-pro-max search index to be installed.
  If you see import errors, your skill installation may be incomplete.
  The full script is bundled with the ui-ux-pro-max skill package.

Usage:
  # Full design system for a project
  python3 search.py "saas dashboard fintech" --design-system -p "MyApp"

  # Domain-specific search
  python3 search.py "dark mode" --domain style -n 5
  python3 search.py "button hover states" --domain ux
  python3 search.py "hero section" --domain landing

  # Stack guidelines
  python3 search.py "tailwind dark mode" --stack html-tailwind

Domains:
  style        Visual style and aesthetic patterns
  color        Color theory and palette references
  chart        Data visualization patterns
  landing      Landing page sections and layouts
  product      Product UI and SaaS patterns
  ux           UX patterns and interaction design
  typography   Font pairings and type scales

Stacks:
  html-tailwind    Vanilla HTML + Tailwind CSS
  react-tailwind   React + Tailwind CSS
  next-tailwind    Next.js + Tailwind CSS
  vue-tailwind     Vue 3 + Tailwind CSS
"""

import argparse
import json
import sys
from pathlib import Path

# ─── Try to import the actual search engine ──────────────────────────────────
try:
    from _search_engine import DesignSearchEngine, generate_design_system
    _ENGINE_AVAILABLE = True
except ImportError:
    _ENGINE_AVAILABLE = False


def fallback_output(query: str, domain: str | None, design_system: bool, project: str | None) -> None:
    """
    When the full search engine isn't available, emit a helpful stub output
    that the skill can still use as a design system skeleton.
    """
    print(f"⚠️  Search engine not available — generating skeleton design system\n")

    if design_system or not domain:
        output = {
            "project": project or "Project",
            "query": query,
            "design_system": {
                "color_palette": {
                    "primary": "#3B82F6",
                    "secondary": "#6366F1",
                    "cta": "#10B981",
                    "background": "#FFFFFF",
                    "surface": "#F8FAFC",
                    "text": "#0F172A",
                    "muted": "#64748B",
                    "border": "#E2E8F0",
                },
                "typography": {
                    "heading_font": "Inter",
                    "body_font": "Inter",
                    "scale": "4xl/3xl/2xl/xl/lg/base/sm",
                },
                "effects": "subtle-shadow, rounded-2xl, smooth-transitions",
                "key_animations": ["fadeInUp", "hover-lift", "smooth-scale"],
                "style_direction": "clean-minimal-professional",
            },
            "note": (
                "Install the full ui-ux-pro-max skill package to get AI-powered design "
                "pattern search. This is a fallback skeleton — replace these tokens with "
                "values appropriate for your project."
            ),
        }
        print(json.dumps(output, indent=2))
    else:
        print(json.dumps({
            "domain": domain,
            "query": query,
            "results": [],
            "note": "Full search engine not available. Install complete skill package.",
        }, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="ui-ux-pro-max design search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--domain", "-d", help="Search domain (style/color/chart/landing/product/ux/typography)")
    parser.add_argument("--design-system", action="store_true", help="Generate full design system")
    parser.add_argument("--stack", "-s", help="Stack guidelines (html-tailwind/react-tailwind/etc.)")
    parser.add_argument("--project", "-p", help="Project name for design system")
    parser.add_argument("-n", "--max-results", type=int, default=5, help="Max results")
    args = parser.parse_args()

    if not _ENGINE_AVAILABLE:
        fallback_output(
            query=args.query,
            domain=args.domain,
            design_system=args.design_system,
            project=args.project,
        )
        return

    # Full engine path
    engine = DesignSearchEngine()

    if args.design_system:
        result = generate_design_system(
            engine=engine,
            query=args.query,
            project_name=args.project or args.query.title(),
        )
    elif args.stack:
        result = engine.search_stack_guidelines(stack=args.stack, query=args.query)
    else:
        result = engine.search(
            query=args.query,
            domain=args.domain,
            max_results=args.max_results,
        )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
