"""
PyProfiler - Simple, Powerful Python Profiling

Zero-dependency, lightweight profiling for Python applications.

Example:
    from pyprofiler import Profiler, time_block, checkpoint
    
    with time_block("operation"):
        do_work()
    
    checkpoint("milestone", count=1000)
    
    # Print summary
    from pyprofiler import print_summary
    print_summary()
"""

__version__ = "1.0.0"
__author__ = "Sankalp Patidar"
__license__ = "MIT"

from .profiler import (
    Profiler,
    TimingRecord,
    get_profiler,
    enable_profiling,
    disable_profiling,
    time_block,
    checkpoint,
    print_summary,
    export_json,
)

__all__ = [
    "Profiler",
    "TimingRecord",
    "get_profiler",
    "enable_profiling",
    "disable_profiling",
    "time_block",
    "checkpoint",
    "print_summary",
    "export_json",
]