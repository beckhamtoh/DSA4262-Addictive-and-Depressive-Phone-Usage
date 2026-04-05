from __future__ import annotations

import argparse
from pathlib import Path
import re

import pandas as pd


INVALID_FILENAME_CHARS = r'[<>:"/\\|?*]'


def _sanitize_for_filename(value: str) -> str:
	cleaned = re.sub(INVALID_FILENAME_CHARS, "_", value.strip())
	cleaned = re.sub(r"\s+", "_", cleaned)
	return cleaned or "sheet"


def excel_to_csv(file_path: str | Path, output_dir: str | Path | None = None) -> list[Path]:
	excel_path = Path(file_path).expanduser().resolve()
	if not excel_path.exists() or not excel_path.is_file():
		raise FileNotFoundError(f"Excel file not found: {excel_path}")

	destination = (
		Path(output_dir).expanduser().resolve()
		if output_dir is not None
		else excel_path.parent
	)
	destination.mkdir(parents=True, exist_ok=True)

	workbook = pd.ExcelFile(excel_path)
	file_stem = _sanitize_for_filename(excel_path.stem)

	created_files: list[Path] = []
	for sheet_name in workbook.sheet_names:
		data = workbook.parse(sheet_name=sheet_name)
		safe_sheet_name = _sanitize_for_filename(sheet_name)
		csv_name = f"{file_stem}_{safe_sheet_name}.csv"
		csv_path = destination / csv_name
		data.to_csv(csv_path, index=False)
		created_files.append(csv_path)

	return created_files


def _build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		description="Convert each sheet in an Excel file into CSV files.",
	)
	parser.add_argument("file_path", help="Path to the input Excel file")
	parser.add_argument(
		"-o",
		"--output-dir",
		help="Directory to write CSV files (defaults to Excel file directory)",
	)
	return parser


def main() -> None:
	parser = _build_parser()
	args = parser.parse_args()

	created_files = excel_to_csv(args.file_path, args.output_dir)
	for file in created_files:
		print(file)


if __name__ == "__main__":
	main()
