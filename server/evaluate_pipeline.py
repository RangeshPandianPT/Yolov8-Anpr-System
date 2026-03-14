import argparse
import os
from collections import Counter
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pipeline import ANPRPipeline


def iter_image_files(root_dir):
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in {"venv", "node_modules", "__pycache__"}]
        for name in files:
            if name.lower().endswith((".jpg", ".jpeg", ".png")):
                yield os.path.join(root, name)


def evaluate_images(image_paths, max_images=None):
    pipeline = ANPRPipeline()

    processed = 0
    success = 0
    total_latency = 0.0
    error_counter = Counter()

    for image_path in image_paths:
        if max_images is not None and processed >= max_images:
            break

        result = pipeline.process_image(image_path)
        processed += 1

        total_latency += float(result.get("processing_time_sec", 0.0))
        if result.get("status") == "success":
            success += 1
        else:
            error_code = result.get("error_code", "unknown_error")
            error_counter[error_code] += 1

    avg_latency = (total_latency / processed) if processed else 0.0
    success_rate = (success / processed * 100.0) if processed else 0.0

    return {
        "processed": processed,
        "success": success,
        "success_rate": round(success_rate, 2),
        "avg_latency_sec": round(avg_latency, 3),
        "error_breakdown": dict(error_counter),
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate ANPR pipeline on a folder of images.")
    parser.add_argument("--images-dir", required=True, help="Directory containing test images")
    parser.add_argument("--max-images", type=int, default=None, help="Limit number of processed images")
    args = parser.parse_args()

    if not os.path.isdir(args.images_dir):
        raise SystemExit(f"Images directory not found: {args.images_dir}")

    image_paths = list(iter_image_files(args.images_dir))
    if not image_paths:
        raise SystemExit(f"No images found in: {args.images_dir}")

    summary = evaluate_images(image_paths, max_images=args.max_images)

    print("=== ANPR Evaluation Summary ===")
    print(f"Processed: {summary['processed']}")
    print(f"Success: {summary['success']}")
    print(f"Success Rate: {summary['success_rate']}%")
    print(f"Average Latency: {summary['avg_latency_sec']} sec")
    print("Error Breakdown:")
    if summary["error_breakdown"]:
        for key, value in summary["error_breakdown"].items():
            print(f"  - {key}: {value}")
    else:
        print("  - none")


if __name__ == "__main__":
    main()
