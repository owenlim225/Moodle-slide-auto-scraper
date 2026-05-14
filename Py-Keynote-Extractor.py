from __future__ import annotations

import argparse
import os
import random
import sys
import time

import requests
from dotenv import load_dotenv


def title_from_base_name(base_name: str) -> str:
    """Human-readable default title: underscores to spaces."""
    return base_name.replace("_", " ").strip() or "Scraped lesson content"


def load_cookie(cookie_file: str | None) -> str:
    """Cookie header value from --cookie-file (first non-empty line) or MOODLE_SESSION_COOKIE (e.g. from .env)."""
    if cookie_file:
        try:
            with open(cookie_file, encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if s:
                        return s
        except OSError as e:
            print(f"Error reading cookie file {cookie_file!r}: {e}", file=sys.stderr)
            sys.exit(1)
        return ""
    return os.environ.get("MOODLE_SESSION_COOKIE", "").strip()


def parse_args() -> argparse.Namespace:
    default_base = "Scraped_Lesson_Content"
    default_title_help = (
        "Document title for the output banner. Default: derived from --base-name "
        "(underscores replaced with spaces), or interactively prompted on a TTY if "
        "--title is omitted (see --base-name)."
    )
    parser = argparse.ArgumentParser(
        description="Download Moodle/lesson JSON slide URLs and extract text into a single .txt file."
    )
    parser.add_argument("--urls-file", default="urls.txt", help="Path to newline-separated slide .json URLs.")
    parser.add_argument(
        "--output-dir",
        default="scraped_outputs",
        help="Directory for output text files (created if missing).",
    )
    parser.add_argument(
        "--base-name",
        default=default_base,
        help="Base filename without extension; numeric suffix added if file exists.",
    )
    parser.add_argument("--title", default=argparse.SUPPRESS, help=default_title_help)
    parser.add_argument(
        "--env-file",
        default=".env",
        metavar="PATH",
        help="Load KEY=value pairs into the process environment before reading MOODLE_* vars (default: .env). "
        "Missing file is ignored. Does not override variables already set in the shell.",
    )
    parser.add_argument(
        "--cookie-file",
        default=None,
        metavar="PATH",
        help="Read Cookie header value from first non-empty line (strips). Overrides MOODLE_SESSION_COOKIE if set.",
    )
    parser.add_argument(
        "--referer",
        default=None,
        help="HTTP Referer header. If omitted, uses env MOODLE_REFERER if set; otherwise no Referer header.",
    )
    parser.add_argument(
        "--user-agent",
        default=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        help="User-Agent header (default: desktop Chrome string).",
    )
    parser.add_argument("--timeout", type=float, default=20.0, help="Per-request timeout in seconds.")
    parser.add_argument("--retries", type=int, default=3, help="Max attempts per slide on failure.")
    parser.add_argument(
        "--delay-min",
        type=float,
        default=1.5,
        help="Minimum delay in seconds between slides (after the first).",
    )
    parser.add_argument(
        "--delay-max",
        type=float,
        default=4.0,
        help="Maximum delay in seconds between slides (after the first).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    load_dotenv(args.env_file, override=False)

    cookie = load_cookie(args.cookie_file)
    if not cookie:
        print(
            "Error: no session cookie provided.\n"
            "  Put MOODLE_SESSION_COOKIE in a .env file (see .env.example), or set it in the environment, or\n"
            "  pass --cookie-file PATH whose first non-empty line is the full Cookie header value "
            '(e.g. "MoodleSession=abc").\n'
            f"  Optional: --env-file PATH (default: .env) to load variables from a file.",
            file=sys.stderr,
        )
        sys.exit(1)

    if hasattr(args, "title"):
        doc_title = args.title
    else:
        derived = title_from_base_name(args.base_name)
        if sys.stdin.isatty():
            try:
                entered = input(f"Document title [{derived}]: ").strip()
                doc_title = entered if entered else derived
            except EOFError:
                doc_title = derived
        else:
            doc_title = derived

    referer = args.referer if args.referer is not None else os.environ.get("MOODLE_REFERER", "").strip() or None

    headers: dict[str, str] = {
        "User-Agent": args.user_agent,
        "Cookie": cookie,
        "Accept": "application/json",
        "Connection": "keep-alive",
    }
    if referer:
        headers["Referer"] = referer

    os.makedirs(args.output_dir, exist_ok=True)

    try:
        with open(args.urls_file, encoding="utf-8") as f:
            urls = [
                line.strip()
                for line in f
                if line.strip().endswith(".json") and "header.json" not in line
            ]
    except FileNotFoundError:
        print(f"Error: urls file {args.urls_file!r} not found.", file=sys.stderr)
        sys.exit(1)

    sep_width = max(len(doc_title), 30)
    all_text = doc_title + "\n" + ("=" * sep_width) + "\n\n"

    def extract_strings(obj):
        found = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in ("text", "string", "textString") and isinstance(v, str):
                    if len(v.strip()) > 1:
                        found.append(v.strip())
                else:
                    found.extend(extract_strings(v))
        elif isinstance(obj, list):
            for item in obj:
                found.extend(extract_strings(item))
        return found

    any_slide_had_text = False
    print(f"Starting extraction for {len(urls)} slides...")

    for i, url in enumerate(urls, 1):
        success = False
        retries = args.retries

        while not success and retries > 0:
            try:
                if i > 1:
                    wait_time = random.uniform(args.delay_min, args.delay_max)
                    time.sleep(wait_time)

                response = requests.get(url, headers=headers, timeout=args.timeout)

                if response.status_code == 200:
                    try:
                        data = response.json()
                    except ValueError as e:
                        print(f"Slide {i}: invalid JSON ({e}). Retries left: {retries - 1}")
                        retries -= 1
                        continue

                    slide_content = extract_strings(data)

                    if slide_content:
                        any_slide_had_text = True
                        unique_content = list(dict.fromkeys(slide_content))
                        all_text += f"Slide {i}\n" + "-" * 10 + "\n" + "\n".join(unique_content) + "\n\n"
                        print(f"Processed slide {i}")
                    else:
                        print(f"Slide {i}: no text found.")

                    success = True

                elif response.status_code == 429:
                    print(f"Rate limited on slide {i}. Sleeping 30s...")
                    time.sleep(30)
                    retries -= 1
                else:
                    print(f"Slide {i} failed with status {response.status_code}. Retries left: {retries - 1}")
                    retries -= 1

            except requests.exceptions.ReadTimeout:
                print(f"Timeout on slide {i}. Retries left: {retries - 1}")
                time.sleep(5)
                retries -= 1
            except requests.RequestException as e:
                print(f"Request error on slide {i}: {e}. Retries left: {retries - 1}")
                retries -= 1
            except OSError as e:
                print(f"Error on slide {i}: {e}. Retries left: {retries - 1}")
                retries -= 1
            except Exception as e:
                print(f"Error on slide {i}: {e}. Retries left: {retries - 1}")
                retries -= 1

    if urls and not any_slide_had_text:
        print(
            "Warning: no slide produced any extracted text, but the URL list was non-empty. "
            "Saving output anyway.",
            file=sys.stderr,
        )

    filename = f"{args.base_name}.txt"
    filepath = os.path.join(args.output_dir, filename)
    counter = 1
    while os.path.exists(filepath):
        filename = f"{args.base_name}_{counter}.txt"
        filepath = os.path.join(args.output_dir, filename)
        counter += 1

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(all_text)

    print(f"Done. Results saved to: {filepath}")


if __name__ == "__main__":
    main()
