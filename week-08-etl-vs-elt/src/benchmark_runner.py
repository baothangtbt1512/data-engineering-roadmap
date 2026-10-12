import json
import random
import psutil
import os
from tabulate import tabulate
from src.pipeline_etl import run_etl_pipeline
from src.pipeline_elt import run_elt_pipeline

def generate_mock_dataset(size=50000):
    print(f"[DATA GEN] Generating {size:,} realistic e-commerce product records...")
    categories = ["smartphones", "laptops", "fragrances", "skincare", "groceries", "home-decoration"]
    dataset = []
    for i in range(1, size + 1):
        dataset.append({
            "id": i,
            "title": f" Product Model {i} Premium Edition ",
            "category": random.choice(categories),
            "price": round(random.uniform(10.0, 2000.0), 2),
            "discountPercentage": round(random.uniform(0.0, 30.0), 2),
            "stock": random.randint(0, 150)
        })
    return dataset

def get_ram_usage_mb():
    process = psutil.Process(os.getpid())
    return round(process.memory_info().rss / (1024 * 1024), 2)

def main():
    print("=" * 65)
    print("      DE BENCHMARK LAB: PIPELINE ETL vs PIPELINE ELT")
    print("=" * 65)

    dataset = generate_mock_dataset(50000)

    # Đo ETL
    ram_before_etl = get_ram_usage_mb()
    res_etl = run_etl_pipeline(dataset)
    ram_after_etl = get_ram_usage_mb()
    res_etl["ram_used_mb"] = round(ram_after_etl - ram_before_etl, 2)

    # Đo ELT
    ram_before_elt = get_ram_usage_mb()
    res_elt = run_elt_pipeline(dataset)
    ram_after_elt = get_ram_usage_mb()
    res_elt["ram_used_mb"] = round(ram_after_elt - ram_before_elt, 2)

    # Tổng hợp bảng so sánh
    table_data = [
        ["Kịch bản (Pipeline)", res_etl["pipeline"], res_elt["pipeline"]],
        ["Tổng số bản ghi", f"{res_etl['rows_processed']:,}", f"{res_elt['rows_processed']:,}"],
        ["Thời gian Transform", f"{res_etl['transform_time_sec']} s (Python)", f"{res_elt['transform_time_sec']} s (Postgres SQL)"],
        ["Thời gian Load", f"{res_etl['load_time_sec']} s", f"{res_elt['load_time_sec']} s (Raw Staging)"],
        ["TỔNG THỜI GIAN THỰC THI", f"{res_etl['total_time_sec']} s", f"{res_elt['total_time_sec']} s"],
        ["RAM tiêu thụ tại Python App", f"{res_etl['ram_used_mb']} MB", f"{res_elt['ram_used_mb']} MB"]
    ]

    print("\n" + tabulate(table_data, headers="firstrow", tablefmt="fancy_grid"))

    # Lưu kết quả json
    benchmark_out = {
        "etl": res_etl,
        "elt": res_elt
    }
    with open("benchmark/results.json", "w", encoding="utf-8") as f:
        json.dump(benchmark_out, f, indent=2)
    print("\n[INFO] Benchmark results saved to benchmark/results.json")

if __name__ == "__main__":
    main()