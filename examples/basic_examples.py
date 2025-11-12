#!/usr/bin/env python3
"""
Test profiling system with a simple example
"""
import time
import asyncio
from extractor.profiler import get_profiler, time_block, checkpoint, print_summary


async def slow_operation_1():
    """Simulate a slow Wikidata query"""
    with time_block("wikidata_query", num_codes=25):
        # Simulate query building
        with time_block("build_query"):
            time.sleep(0.1)
        
        # Simulate HTTP request
        with time_block("http_request"):
            checkpoint("sending_request", endpoint="wikidata")
            time.sleep(2.0)  # Simulate network delay
        
        # Simulate JSON parsing
        with time_block("json_parse"):
            time.sleep(0.5)


async def slow_operation_2():
    """Simulate geographic data fetching"""
    with time_block("fetch_geo_data", num_codes=25):
        # Process in chunks
        for i in range(3):
            with time_block(f"geo_chunk_{i+1}", chunk_size=8):
                time.sleep(1.5)
                checkpoint(f"chunk_{i+1}_complete", codes_processed=8)


async def fast_operation():
    """Simulate fast operations"""
    with time_block("merge_languages", num_langs=25):
        for i in range(25):
            with time_block("merge_single_language"):
                time.sleep(0.01)  # Very fast


async def main():
    print("🔍 Testing Profiling System")
    print("=" * 60)
    print("\nRunning simulated operations...\n")
    
    profiler = get_profiler()
    
    # Simulate a batch processing loop
    for batch_num in range(1, 3):
        print(f"Processing batch {batch_num}...")
        
        with time_block("process_batch", batch_num=batch_num):
            # Slow operation 1
            await slow_operation_1()
            
            # Slow operation 2
            await slow_operation_2()
            
            # Fast operation
            await fast_operation()
            
        checkpoint(f"batch_{batch_num}_complete", num_languages=25)
        
        # Pause between batches
        await asyncio.sleep(0.5)
    
    # Print summary
    print("\n" + "=" * 60)
    print_summary(top_n=20)
    
    # Export
    profiler.export_json("test_profiling.json")
    print("\n✅ Test complete! Check test_profiling.json")
    print("📊 Run: python scripts/analyze_profile.py test_profiling.json")


if __name__ == "__main__":
    asyncio.run(main())