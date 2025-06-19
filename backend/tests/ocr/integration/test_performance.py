"""
Integration Tests for OCR Performance and Benchmarking.

This module contains performance-focused integration tests for the OCR service.
"""

import pytest
import time
import statistics
from typing import List, Dict, Any

from domains.ocr.services import extract_text_from_image, process_receipt_image
from tests.ocr.config import OCRTestConfig


# Skip if not in integration mode
pytestmark = pytest.mark.skipif(
    not OCRTestConfig.should_run_integration_tests(),
    reason="Performance tests require tesseract and INTEGRATION_MODE=true"
)


class TestOCRPerformance:
    """Performance and benchmarking tests for OCR functionality."""

    @classmethod
    def setup_class(cls):
        """Setup class and log performance test context."""
        print(OCRTestConfig.log_performance_context())

    @pytest.mark.asyncio
    async def test_ocr_latency_benchmarks(self):
        """Benchmark OCR latency across different image types."""
        config = OCRTestConfig()
        
        # Test different image variants
        test_cases = [
            ("sample_receipt.png", "clean_receipt"),
            ("sample_receipt_blurred.png", "blurred_receipt"),
            ("sample_receipt_rotated.png", "rotated_receipt"),
        ]
        
        latency_results = {}
        
        for image_name, test_type in test_cases:
            image_path = config.get_sample_image_path(image_name)
            
            if image_path and image_path.exists():
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                # Run multiple iterations for statistical significance
                latencies = []
                for _ in range(5):
                    start_time = time.time()
                    result = await extract_text_from_image(image_data)
                    end_time = time.time()
                    
                    latencies.append((end_time - start_time) * 1000)  # Convert to milliseconds
                    assert result.extracted_text is not None
                
                # Calculate statistics
                avg_latency = statistics.mean(latencies)
                std_dev = statistics.stdev(latencies) if len(latencies) > 1 else 0
                
                latency_results[test_type] = {
                    'avg_ms': avg_latency,
                    'std_dev_ms': std_dev,
                    'min_ms': min(latencies),
                    'max_ms': max(latencies),
                    'samples': latencies
                }
                
                # Performance assertions - using configurable thresholds
                max_avg_latency = OCRTestConfig.get_performance_threshold('avg_latency_ms')
                max_std_dev = OCRTestConfig.get_performance_threshold('latency_std_dev_ms')
                
                assert avg_latency < max_avg_latency, \
                    f"{test_type}: Average latency {avg_latency:.1f}ms exceeds threshold {max_avg_latency}ms"
                assert std_dev < max_std_dev, \
                    f"{test_type}: Latency variance {std_dev:.1f}ms exceeds threshold {max_std_dev}ms"
        
        # Log performance results for analysis
        for test_type, stats in latency_results.items():
            print(f"\n{test_type} Performance:")
            print(f"  Average: {stats['avg_ms']:.1f}ms")
            print(f"  Std Dev: {stats['std_dev_ms']:.1f}ms")
            print(f"  Range: {stats['min_ms']:.1f}ms - {stats['max_ms']:.1f}ms")

    @pytest.mark.asyncio
    async def test_ocr_throughput_under_load(self):
        """Test OCR throughput under concurrent load."""
        import asyncio
        
        config = OCRTestConfig()
        image_path = config.get_sample_image_path("sample_receipt.png")
        
        if image_path and image_path.exists():
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Test different concurrency levels
            concurrency_levels = [1, 2, 3, 5]
            
            for concurrency in concurrency_levels:
                start_time = time.time()
                
                # Create concurrent tasks
                tasks = [
                    extract_text_from_image(image_data) 
                    for _ in range(concurrency)
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                end_time = time.time()
                total_time = end_time - start_time
                
                # Verify all completed successfully
                successful_results = [r for r in results if not isinstance(r, Exception)]
                assert len(successful_results) == concurrency, \
                    f"Only {len(successful_results)}/{concurrency} tasks completed successfully"
                
                # Calculate throughput
                throughput = concurrency / total_time  # tasks per second
                
                print(f"\nConcurrency {concurrency}: {throughput:.2f} tasks/second")
                
                # Performance expectations - using configurable thresholds
                min_throughput = OCRTestConfig.get_performance_threshold('min_throughput_tps')
                max_total_time = OCRTestConfig.get_performance_threshold('throughput_total_time_s')
                
                assert throughput > min_throughput, \
                    f"Throughput too low: {throughput:.2f} tasks/second (min: {min_throughput})"
                assert total_time < max_total_time, \
                    f"Total time too high: {total_time:.1f} seconds (max: {max_total_time}s)"

    @pytest.mark.asyncio
    async def test_memory_usage_over_time(self):
        """Test memory usage patterns over extended OCR operations."""
        import gc
        import psutil
        import os
        
        config = OCRTestConfig()
        image_path = config.get_sample_image_path("sample_receipt.png")
        
        if image_path and image_path.exists():
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Get initial memory usage
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            memory_samples = [initial_memory]
            
            # Process images repeatedly
            for i in range(10):
                result = await extract_text_from_image(image_data)
                assert result.extracted_text is not None
                
                # Sample memory every few iterations
                if i % 2 == 0:
                    gc.collect()  # Force garbage collection
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_samples.append(current_memory)
            
            # Analyze memory usage
            max_memory = max(memory_samples)
            memory_growth = max_memory - initial_memory
            
            print(f"\nMemory Usage Analysis:")
            print(f"  Initial: {initial_memory:.1f}MB")
            print(f"  Peak: {max_memory:.1f}MB")
            print(f"  Growth: {memory_growth:.1f}MB")
            
            # Memory growth should be reasonable - using configurable threshold
            max_memory_growth = OCRTestConfig.get_performance_threshold('memory_growth_mb')
            assert memory_growth < max_memory_growth, \
                f"Excessive memory growth: {memory_growth:.1f}MB (max: {max_memory_growth}MB)"

    @pytest.mark.asyncio
    async def test_ocr_accuracy_vs_speed_tradeoffs(self):
        """Test accuracy vs speed tradeoffs in OCR configuration."""
        from domains.ocr.services import OCRService
        
        config = OCRTestConfig()
        image_path = config.get_sample_image_path("sample_receipt.png")
        
        if image_path and image_path.exists():
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            service = OCRService()
            
            # Test different OCR configurations
            configs = [
                ("fast", "--psm 6 --oem 1"),
                ("balanced", "--psm 6 --oem 1 -c tesseract_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,$()- "),
                ("accurate", "--psm 4 --oem 1 -c tesseract_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,$()- "),
            ]
            
            results = {}
            
            for config_name, config_string in configs:
                # Mock the optimal config to test specific configurations
                original_config = service.optimal_config
                service.optimal_config = {'primary': config_string}
                
                try:
                    start_time = time.time()
                    result = await service.extract_text_from_image(image_data)
                    processing_time = (time.time() - start_time) * 1000
                    
                    results[config_name] = {
                        'processing_time_ms': processing_time,
                        'confidence': result.confidence,
                        'text_length': len(result.extracted_text),
                        'text': result.extracted_text
                    }
                    
                finally:
                    service.optimal_config = original_config
            
            # Analyze results
            for config_name, stats in results.items():
                print(f"\n{config_name} Configuration:")
                print(f"  Time: {stats['processing_time_ms']:.1f}ms")
                print(f"  Confidence: {stats['confidence']:.1f}%")
                print(f"  Text Length: {stats['text_length']} chars")
            
            # Verify all configurations produced reasonable results
            for config_name, stats in results.items():
                assert stats['processing_time_ms'] > 0, f"{config_name}: Invalid processing time"
                assert stats['confidence'] >= 0, f"{config_name}: Invalid confidence score"
                assert stats['text_length'] > 0, f"{config_name}: No text extracted"

    @pytest.mark.asyncio
    async def test_end_to_end_processing_performance(self):
        """Test complete end-to-end processing performance."""
        config = OCRTestConfig()
        image_path = config.get_sample_image_path("sample_receipt.png")
        
        if image_path and image_path.exists():
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Measure complete workflow
            processing_times = []
            
            for _ in range(3):
                start_time = time.time()
                result = await process_receipt_image(image_data)
                end_time = time.time()
                
                processing_time = (end_time - start_time) * 1000
                processing_times.append(processing_time)
                
                # Verify result quality
                assert result.total_items_detected >= 0
                assert result.processing_time_ms is not None and result.processing_time_ms > 0
                assert result.raw_text is not None
            
            # Analyze performance
            avg_time = statistics.mean(processing_times)
            max_time = max(processing_times)
            min_time = min(processing_times)
            
            print(f"\nEnd-to-End Performance:")
            print(f"  Average: {avg_time:.1f}ms")
            print(f"  Range: {min_time:.1f}ms - {max_time:.1f}ms")
            
            # Performance expectations for complete workflow - using configurable thresholds
            max_avg_time = OCRTestConfig.get_performance_threshold('e2e_avg_time_ms')
            max_worst_time = OCRTestConfig.get_performance_threshold('e2e_max_time_ms')
            
            assert avg_time < max_avg_time, \
                f"End-to-end processing too slow: {avg_time:.1f}ms (max: {max_avg_time}ms)"
            assert max_time < max_worst_time, \
                f"Worst case too slow: {max_time:.1f}ms (max: {max_worst_time}ms)"

    @pytest.mark.asyncio
    async def test_scalability_with_image_sizes(self):
        """Test how OCR performance scales with different image sizes."""
        from PIL import Image
        import io
        
        config = OCRTestConfig()
        base_image_path = config.get_sample_image_path("sample_receipt.png")
        
        if base_image_path and base_image_path.exists():
            # Load and resize to different sizes
            with Image.open(base_image_path) as base_img:
                size_variants = [
                    (0.5, "small"),
                    (1.0, "original"),
                    (1.5, "large"),
                ]
                
                performance_data = {}
                
                for scale_factor, size_name in size_variants:
                    # Resize image
                    new_size = (
                        int(base_img.width * scale_factor),
                        int(base_img.height * scale_factor)
                    )
                    
                    resized_img = base_img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Convert to bytes
                    img_buffer = io.BytesIO()
                    resized_img.save(img_buffer, format='PNG')
                    img_data = img_buffer.getvalue()
                    
                    # Measure performance
                    start_time = time.time()
                    result = await extract_text_from_image(img_data)
                    processing_time = (time.time() - start_time) * 1000
                    
                    performance_data[size_name] = {
                        'size': new_size,
                        'file_size_kb': len(img_data) / 1024,
                        'processing_time_ms': processing_time,
                        'confidence': result.confidence,
                        'text_length': len(result.extracted_text)
                    }
                
                # Analyze scalability
                for size_name, data in performance_data.items():
                    print(f"\n{size_name} Image ({data['size'][0]}x{data['size'][1]}):")
                    print(f"  File Size: {data['file_size_kb']:.1f}KB")
                    print(f"  Processing Time: {data['processing_time_ms']:.1f}ms")
                    print(f"  Confidence: {data['confidence']:.1f}%")
                
                # Verify performance scaling is reasonable - using configurable threshold
                max_processing_time = OCRTestConfig.get_performance_threshold('scalability_max_time_ms')
                
                for size_name, data in performance_data.items():
                    assert data['processing_time_ms'] < max_processing_time, \
                        f"{size_name}: Processing time {data['processing_time_ms']:.1f}ms exceeds threshold {max_processing_time}ms"
