#!/usr/bin/env python3
"""
Analyze profiling data to identify bottlenecks
"""
import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List


def load_profile(filepath: str) -> Dict:
    """Load profiling JSON"""
    return json.loads(Path(filepath).read_text())


def analyze_bottlenecks(profile: Dict) -> Dict:
    """Identify the slowest operations"""
    records = profile.get("records", [])
    
    # Group by operation name
    by_operation = defaultdict(list)
    for record in records:
        name = record["name"]
        duration = record["duration_seconds"]
        
        # Skip checkpoints
        if "CHECKPOINT" in name:
            continue
        
        # Extract top-level operation
        top_level = name.split(" > ")[0]
        by_operation[top_level].append(duration)
    
    # Calculate statistics
    stats = {}
    for op, durations in by_operation.items():
        stats[op] = {
            "total": sum(durations),
            "count": len(durations),
            "avg": sum(durations) / len(durations),
            "min": min(durations),
            "max": max(durations),
            "median": sorted(durations)[len(durations)//2] if durations else 0
        }
    
    return stats


def print_analysis(profile: Dict):
    """Print comprehensive analysis"""
    total_time = profile.get("total_time", 0)
    num_ops = profile.get("num_operations", 0)
    
    print("=" * 80)
    print("🔍 PROFILING ANALYSIS")
    print("=" * 80)
    print(f"\nTotal Time: {total_time:.2f}s ({total_time/60:.2f}m)")
    print(f"Total Operations: {num_ops}")
    
    # Get statistics
    stats = analyze_bottlenecks(profile)
    
    # Sort by total time
    sorted_ops = sorted(stats.items(), key=lambda x: -x[1]["total"])
    
    print(f"\n{'Operation':<40} {'Total':<12} {'Calls':<8} {'Avg':<12} {'Max':<12} {'%':<8}")
    print("-" * 80)
    
    for op, data in sorted_ops[:20]:
        pct = (data["total"] / total_time * 100) if total_time > 0 else 0
        print(f"{op:<40} {data['total']:>8.2f}s    {data['count']:<8} "
              f"{data['avg']:>8.2f}s    {data['max']:>8.2f}s    {pct:>6.1f}%")
    
    # Identify bottlenecks
    print("\n" + "=" * 80)
    print("🚨 TOP BOTTLENECKS")
    print("=" * 80)
    
    bottlenecks = []
    for op, data in sorted_ops:
        # Bottleneck if: takes >10% of time or avg >5s
        pct = (data["total"] / total_time * 100) if total_time > 0 else 0
        if pct > 10 or data["avg"] > 5:
            bottlenecks.append((op, data, pct))
    
    if not bottlenecks:
        print("\n✅ No major bottlenecks found!")
    else:
        for i, (op, data, pct) in enumerate(bottlenecks, 1):
            print(f"\n{i}. {op}")
            print(f"   Total time: {data['total']:.2f}s ({pct:.1f}% of build)")
            print(f"   Called: {data['count']} times")
            print(f"   Average: {data['avg']:.2f}s per call")
            print(f"   Max: {data['max']:.2f}s")
            
            # Suggest optimizations
            if "wikidata" in op.lower():
                print(f"   💡 Optimization: Increase batch size or reduce timeout")
            elif "glottolog" in op.lower():
                print(f"   💡 Optimization: Batch Glottolog requests if possible")
            elif "geo" in op.lower():
                print(f"   💡 Optimization: Reduce chunk_size or increase timeout")
            elif "parse" in op.lower():
                print(f"   💡 Optimization: This is usually fast, check data size")
            elif "merge" in op.lower():
                print(f"   💡 Optimization: This is usually fast, check related language logic")
    
    # Timeline analysis
    print("\n" + "=" * 80)
    print("📈 TIMELINE ANALYSIS")
    print("=" * 80)
    
    records = profile.get("records", [])
    if records:
        # Group by 10-second buckets
        buckets = defaultdict(lambda: {"count": 0, "total": 0.0})
        
        first_time = min(r.get("start_time", "9999") for r in records if "CHECKPOINT" not in r.get("name", ""))
        
        for record in records:
            if "CHECKPOINT" in record.get("name", ""):
                continue
            
            start = record.get("start_time", "")
            if not start:
                continue
            
            # Parse ISO timestamp
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                first_dt = datetime.fromisoformat(first_time.replace("Z", "+00:00"))
                elapsed = (dt - first_dt).total_seconds()
                bucket = int(elapsed / 10) * 10  # 10-second buckets
                
                buckets[bucket]["count"] += 1
                buckets[bucket]["total"] += record.get("duration_seconds", 0)
            except:
                pass
        
        if buckets:
            print("\nActivity by time (10s buckets):")
            print(f"{'Time':<12} {'Operations':<12} {'Total Time':<12}")
            print("-" * 40)
            
            for bucket in sorted(buckets.keys())[:30]:  # First 5 minutes
                data = buckets[bucket]
                print(f"{bucket:>4}s-{bucket+10:<3}s {data['count']:>8}      {data['total']:>8.2f}s")


def print_recommendations(profile: Dict):
    """Print optimization recommendations"""
    stats = analyze_bottlenecks(profile)
    total_time = profile.get("total_time", 0)
    
    print("\n" + "=" * 80)
    print("💡 OPTIMIZATION RECOMMENDATIONS")
    print("=" * 80)
    
    recommendations = []
    
    # Check Wikidata
    wd_ops = {k: v for k, v in stats.items() if "wikidata" in k.lower()}
    if wd_ops:
        wd_total = sum(v["total"] for v in wd_ops.values())
        wd_pct = (wd_total / total_time * 100) if total_time > 0 else 0
        
        if wd_pct > 50:
            recommendations.append({
                "priority": "HIGH",
                "area": "Wikidata queries",
                "issue": f"Taking {wd_pct:.1f}% of total time",
                "actions": [
                    "Increase --batch-size (currently determines query size)",
                    "Reduce timeout if queries succeed quickly",
                    "Check if cache is being used effectively",
                    "Consider running during off-peak hours"
                ]
            })
    
    # Check Glottolog
    gl_ops = {k: v for k, v in stats.items() if "glottolog" in k.lower()}
    if gl_ops:
        gl_total = sum(v["total"] for v in gl_ops.values())
        gl_avg = gl_total / sum(v["count"] for v in gl_ops.values())
        
        if gl_avg > 1.0:
            recommendations.append({
                "priority": "MEDIUM",
                "area": "Glottolog fetching",
                "issue": f"Average {gl_avg:.2f}s per request",
                "actions": [
                    "Glottolog API may be slow or rate-limited",
                    "Consider caching Glottolog data locally",
                    "Reduce pause_between if set too high"
                ]
            })
    
    # Check geo
    geo_ops = {k: v for k, v in stats.items() if "geo" in k.lower()}
    if geo_ops:
        geo_total = sum(v["total"] for v in geo_ops.values())
        geo_pct = (geo_total / total_time * 100) if total_time > 0 else 0
        
        if geo_pct > 30:
            recommendations.append({
                "priority": "MEDIUM",
                "area": "Geographic data",
                "issue": f"Taking {geo_pct:.1f}% of total time",
                "actions": [
                    "Geo queries are complex - this is expected",
                    "Reduce chunk_size (currently 6) if timeouts occur",
                    "Increase max_batch_seconds to avoid timeouts"
                ]
            })
    
    # Print recommendations
    if not recommendations:
        print("\n✅ Build performance looks good! No major issues detected.")
    else:
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. [{rec['priority']}] {rec['area']}")
            print(f"   Issue: {rec['issue']}")
            print(f"   Actions:")
            for action in rec['actions']:
                print(f"      • {action}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_profile.py <profiling.json>")
        print("\nExample:")
        print("  python analyze_profile.py data/profiling.json")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    if not Path(filepath).exists():
        print(f"❌ File not found: {filepath}")
        print("\nTo generate profiling data:")
        print("  python -m scripts.build_incremental --profile")
        sys.exit(1)
    
    profile = load_profile(filepath)
    print_analysis(profile)
    print_recommendations(profile)
    
    print("\n" + "=" * 80)
    print("📊 Analysis complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()