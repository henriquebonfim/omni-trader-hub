#!/usr/bin/env python3
"""
PO Lifecycle — Visual Product Review via Playwright

Takes screenshots of every route in the running app, detects broken layouts,
error states, and console errors. Outputs a structured visual-review.json.

Usage:
  python3 playwright_review.py \
    --url http://localhost:$PORT \
    --routes '[]' \
    --output-dir tmp/screenshots/

  # With explicit routes JSON file
  python3 playwright_review.py \
    --url http://localhost:$PORT \
    --routes-file routes.json \
    --output-dir tmp/screenshots/
"""

import argparse
import json
import sys
import time
from pathlib import Path


def detect_routes_from_source() -> list[str]:
    """
    Fallback: try to detect routes from common router config files.
    Returns a list of route paths.
    """
    import re
    routes = {"/"}  # Always include root

    # Next.js app/pages directory
    for pattern in ["app/**/page.tsx", "app/**/page.jsx", "pages/**/*.tsx", "pages/**/*.jsx", "pages/**/*.ts", "pages/**/*.js"]:
        for p in Path(".").glob(pattern):
            # Convert file path to route
            route_path = str(p)
            route_path = re.sub(r"(app|pages)/", "", route_path)
            route_path = re.sub(r"/page\.(tsx|jsx|ts|js)$", "", route_path)
            route_path = re.sub(r"\.(tsx|jsx|ts|js)$", "", route_path)
            route_path = re.sub(r"\[([^\]]+)\]", "_param_", route_path)
            if not route_path.startswith("/"):
                route_path = "/" + route_path
            if "_param_" not in route_path:  # Skip dynamic routes for now
                routes.add(route_path)

    # React Router style: path="..."
    for src_file in Path(".").glob("src/**/*.{tsx,jsx,ts,js}"):
        try:
            content = src_file.read_text(errors="ignore")
            matches = re.findall(r'(?:path|to)=["\'](/[^"\']*)["\']', content)
            for m in matches:
                if not any(c in m for c in ["{", ":", "*"]):  # Skip dynamic
                    routes.add(m)
        except Exception:
            pass

    return sorted(routes)[:20]  # Cap at 20 routes


def run_playwright_review(
    base_url: str,
    routes: list[str],
    output_dir: Path,
    timeout_ms: int = 10000,
) -> list[dict]:
    """
    Run Playwright review. Returns list of finding dicts.
    """
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        print("ERROR: playwright not installed. Run: pip install playwright && python -m playwright install chromium")
        return []

    output_dir.mkdir(parents=True, exist_ok=True)
    findings = []

    print(f"\nStarting visual review of {base_url}")
    print(f"Routes to review: {routes}")
    print(f"Screenshots → {output_dir}\n")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1,
        )

        page = context.new_page()

        # Collect console errors
        console_errors: list[str] = []
        page.on("console", lambda msg: console_errors.append(f"{msg.type}: {msg.text}") if msg.type in ["error", "warning"] else None)

        for route in routes:
            url = f"{base_url.rstrip('/')}{route}"
            route_slug = route.strip("/").replace("/", "_") or "home"
            screenshot_path = output_dir / f"{route_slug}.png"

            console_errors.clear()
            route_issues = []
            status = "OK"

            print(f"  → {url}")

            try:
                response = page.goto(url, timeout=timeout_ms, wait_until="networkidle")

                # Check HTTP status
                if response and response.status >= 400:
                    route_issues.append(f"HTTP {response.status}")
                    status = "BROKEN"

                # Wait for main content
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=5000)
                    time.sleep(0.5)  # Brief settle time for animations
                except Exception:
                    pass

                # Take screenshot
                page.screenshot(path=str(screenshot_path), full_page=True)
                print(f"    📸 {screenshot_path.name}")

                # Check for common error states in DOM
                error_selectors = [
                    "text=404",
                    "text=Not Found",
                    "text=500",
                    "text=Internal Server Error",
                    "text=Error",
                    "[data-testid='error']",
                    ".error-boundary",
                    "#error",
                ]
                for selector in error_selectors:
                    try:
                        elem = page.locator(selector).first
                        if elem.is_visible(timeout=500):
                            text = elem.text_content(timeout=500) or selector
                            route_issues.append(f"Error state visible: {text[:80]}")
                            status = "BROKEN"
                            break
                    except Exception:
                        pass

                # Check for blank/empty page
                body_text = page.locator("body").text_content(timeout=2000) or ""
                if len(body_text.strip()) < 20:
                    route_issues.append("Page appears blank (< 20 chars visible)")
                    status = "BROKEN"

                # Check console errors
                real_errors = [e for e in console_errors if "error" in e.lower() and "favicon" not in e.lower()]
                if real_errors:
                    route_issues.extend(real_errors[:3])
                    if status == "OK":
                        status = "WARNING"

            except PWTimeout:
                route_issues.append(f"Timeout loading {url} ({timeout_ms}ms)")
                status = "BROKEN"
                # Still take a screenshot of whatever loaded
                try:
                    page.screenshot(path=str(screenshot_path))
                except Exception:
                    pass

            except Exception as e:
                route_issues.append(f"Navigation error: {str(e)[:100]}")
                status = "BROKEN"

            findings.append({
                "route": route,
                "url": url,
                "screenshot_path": str(screenshot_path),
                "status": status,
                "issues_found": route_issues,
            })

            # Summary line
            icon = "✅" if status == "OK" else "⚠️" if status == "WARNING" else "❌"
            print(f"    {icon} {status}" + (f" — {route_issues[0]}" if route_issues else ""))

        context.close()
        browser.close()

    return findings


def check_server_reachable(url: str, timeout: int = 5) -> bool:
    """Quick check if the dev server is responding."""
    try:
        import urllib.request
        urllib.request.urlopen(url, timeout=timeout)
        return True
    except Exception:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Visual product review via Playwright")
    parser.add_argument("--url", default="http://localhost:3000", help="Base URL of running app")
    parser.add_argument("--routes", default="[]", help="JSON array of route paths")
    parser.add_argument("--routes-file", default=None, help="JSON file with route paths array")
    parser.add_argument("--output-dir", required=True, help="Directory for screenshots + report")
    parser.add_argument("--timeout", type=int, default=10000, help="Navigation timeout in ms")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    # Load routes
    routes = []
    if args.routes_file and Path(args.routes_file).exists():
        routes = json.loads(Path(args.routes_file).read_text())
    else:
        try:
            routes = json.loads(args.routes)
        except Exception:
            routes = []

    # Auto-detect routes if none provided
    if not routes:
        print("No routes provided — auto-detecting from source files...")
        routes = detect_routes_from_source()
        print(f"Detected {len(routes)} routes: {routes}")

    # Check if server is running
    if not check_server_reachable(args.url):
        print(f"\n⚠️  Server not reachable at {args.url}")
        print("   Start your dev server first:")
        print("   npm run dev | python manage.py runserver | docker compose up -d")
        print("\n   Writing empty visual-review.json...")

        report = {
            "server_reachable": False,
            "base_url": args.url,
            "routes_checked": 0,
            "findings": [],
            "summary": f"Server not reachable at {args.url}",
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir.parent / "visual-review.json").write_text(json.dumps(report, indent=2))
        sys.exit(0)

    # Run review
    findings = run_playwright_review(
        base_url=args.url,
        routes=routes,
        output_dir=output_dir,
        timeout_ms=args.timeout,
    )

    # Write report
    ok_count      = sum(1 for f in findings if f["status"] == "OK")
    warning_count = sum(1 for f in findings if f["status"] == "WARNING")
    broken_count  = sum(1 for f in findings if f["status"] == "BROKEN")

    report = {
        "server_reachable": True,
        "base_url": args.url,
        "routes_checked": len(findings),
        "ok": ok_count,
        "warnings": warning_count,
        "broken": broken_count,
        "findings": findings,
        "summary": f"{ok_count} OK, {warning_count} warnings, {broken_count} broken",
    }

    report_path = output_dir.parent / "visual-review.json"
    report_path.write_text(json.dumps(report, indent=2))

    print(f"\n{'─' * 56}")
    print(f"  VISUAL REVIEW COMPLETE")
    print(f"  ✅ OK:       {ok_count}")
    print(f"  ⚠️  Warnings: {warning_count}")
    print(f"  ❌ Broken:   {broken_count}")
    print(f"  📸 Screenshots: {output_dir}/")
    print(f"  📄 Report: {report_path}")
    print(f"{'─' * 56}")


if __name__ == "__main__":
    main()
