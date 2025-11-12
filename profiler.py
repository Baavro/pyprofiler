"""
Profiling and debugging utilities for the extraction pipeline
"""
import time
import functools
from typing import Dict, List, Optional, Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path


@dataclass
class TimingRecord:
    """Record of a timed operation"""
    name: str
    start_time: float
    end_time: float
    duration: float
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(self.end_time).isoformat(),
            "duration_seconds": round(self.duration, 3),
            "metadata": self.metadata
        }


class Profiler:
    """
    Lightweight profiler for tracking execution time.
    
    Usage:
        profiler = Profiler()
        
        # Context manager
        with profiler.time("fetch_wikidata"):
            result = fetch_data()
        
        # Decorator
        @profiler.track
        def slow_function():
            ...
        
        # Print summary
        profiler.print_summary()
    """
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.records: List[TimingRecord] = []
        self._stack: List[str] = []  # For nested timing
    
    @contextmanager
    def time(self, name: str, **metadata):
        """
        Time a block of code.
        
        Example:
            with profiler.time("fetch_batch", batch_size=25):
                data = fetch_batch(codes)
        """
        if not self.enabled:
            yield
            return
        
        # Handle nested timing
        full_name = " > ".join(self._stack + [name]) if self._stack else name
        self._stack.append(name)
        
        start = time.time()
        try:
            yield
        finally:
            end = time.time()
            duration = end - start
            
            record = TimingRecord(
                name=full_name,
                start_time=start,
                end_time=end,
                duration=duration,
                metadata=metadata
            )
            self.records.append(record)
            self._stack.pop()
            
            # Real-time feedback for long operations
            if duration > 5.0:
                print(f"⏱️  {full_name}: {duration:.2f}s {metadata}")
    
    def track(self, func: Callable) -> Callable:
        """
        Decorator to time a function.
        
        Example:
            @profiler.track
            def fetch_wikidata(codes):
                ...
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self.time(func.__name__):
                return func(*args, **kwargs)
        return wrapper
    
    def checkpoint(self, name: str, **metadata):
        """
        Mark a checkpoint without timing.
        
        Example:
            profiler.checkpoint("batch_1_complete", codes_processed=25)
        """
        if not self.enabled:
            return
        
        record = TimingRecord(
            name=f"CHECKPOINT: {name}",
            start_time=time.time(),
            end_time=time.time(),
            duration=0.0,
            metadata=metadata
        )
        self.records.append(record)
        print(f"📍 {name} {metadata}")
    
    def print_summary(self, top_n: int = 20):
        """Print timing summary"""
        if not self.records:
            print("No timing data collected")
            return
        
        print("\n" + "=" * 80)
        print("⏱️  PROFILING SUMMARY")
        print("=" * 80)
        
        # Total time
        total_time = sum(r.duration for r in self.records if "CHECKPOINT" not in r.name)
        print(f"\n📊 Total Time: {total_time:.2f}s ({total_time/60:.2f}m)")
        
        # Group by top-level operation
        by_operation = {}
        for record in self.records:
            if "CHECKPOINT" in record.name:
                continue
            
            # Extract top-level operation (before first " > ")
            top_level = record.name.split(" > ")[0]
            if top_level not in by_operation:
                by_operation[top_level] = {"total": 0.0, "count": 0, "records": []}
            
            by_operation[top_level]["total"] += record.duration
            by_operation[top_level]["count"] += 1
            by_operation[top_level]["records"].append(record)
        
        # Print by operation
        print(f"\n{'Operation':<40} {'Total Time':<12} {'Calls':<8} {'Avg Time':<12} {'%':<8}")
        print("-" * 80)
        
        sorted_ops = sorted(by_operation.items(), key=lambda x: -x[1]["total"])
        for op_name, data in sorted_ops[:top_n]:
            total = data["total"]
            count = data["count"]
            avg = total / count if count > 0 else 0
            pct = (total / total_time * 100) if total_time > 0 else 0
            
            print(f"{op_name:<40} {total:>8.2f}s    {count:<8} {avg:>8.2f}s    {pct:>6.1f}%")
        
        # Show slowest individual operations
        print(f"\n{'Slowest Operations':<60} {'Time':<12}")
        print("-" * 80)
        
        all_records = [r for r in self.records if "CHECKPOINT" not in r.name]
        slowest = sorted(all_records, key=lambda x: -x.duration)[:10]
        
        for record in slowest:
            name = record.name if len(record.name) <= 57 else record.name[:54] + "..."
            meta_str = f" {record.metadata}" if record.metadata else ""
            print(f"{name:<60} {record.duration:>8.2f}s{meta_str}")
        
        # Checkpoints
        checkpoints = [r for r in self.records if "CHECKPOINT" in r.name]
        if checkpoints:
            print(f"\n📍 Checkpoints:")
            for cp in checkpoints:
                print(f"   {cp.name} {cp.metadata}")
        
        print("=" * 80 + "\n")
    
    def export_json(self, filepath: str):
        """Export timing data to JSON"""
        data = {
            "total_time": sum(r.duration for r in self.records),
            "num_operations": len(self.records),
            "records": [r.to_dict() for r in self.records]
        }
        
        Path(filepath).write_text(json.dumps(data, indent=2))
        print(f"📁 Exported profiling data to {filepath}")
    
    def get_stats(self) -> Dict:
        """Get statistics dictionary"""
        if not self.records:
            return {}
        
        by_operation = {}
        for record in self.records:
            if "CHECKPOINT" in record.name:
                continue
            
            top_level = record.name.split(" > ")[0]
            if top_level not in by_operation:
                by_operation[top_level] = []
            by_operation[top_level].append(record.duration)
        
        stats = {}
        for op, durations in by_operation.items():
            stats[op] = {
                "total": sum(durations),
                "count": len(durations),
                "avg": sum(durations) / len(durations),
                "min": min(durations),
                "max": max(durations)
            }
        
        return stats


# Global profiler instance (can be enabled/disabled)
_global_profiler: Optional[Profiler] = None


def get_profiler() -> Profiler:
    """Get or create global profiler"""
    global _global_profiler
    if _global_profiler is None:
        _global_profiler = Profiler(enabled=True)
    return _global_profiler


def enable_profiling():
    """Enable profiling globally"""
    global _global_profiler
    _global_profiler = Profiler(enabled=True)


def disable_profiling():
    """Disable profiling globally"""
    global _global_profiler
    if _global_profiler:
        _global_profiler.enabled = False


def time_block(name: str, **metadata):
    """Convenient context manager for timing"""
    return get_profiler().time(name, **metadata)


def checkpoint(name: str, **metadata):
    """Convenient checkpoint marker"""
    get_profiler().checkpoint(name, **metadata)


def print_summary(top_n: int = 20):
    """Print profiling summary"""
    get_profiler().print_summary(top_n=top_n)


def export_json(filepath: str):
    """Export profiling data"""
    get_profiler().export_json(filepath)