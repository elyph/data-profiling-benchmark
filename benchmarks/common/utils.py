import os


def get_project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def ensure_output_dir(subdir):
    p = os.path.join(get_project_root(), "benchmark_outputs", subdir)
    os.makedirs(p, exist_ok=True)
    return p
