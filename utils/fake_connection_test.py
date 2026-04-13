"""
Fake Speed Test Data Generator

This script generates realistic fake speed test data based on the structure
of actual speedtest-cli JSON output files. Useful for:
- Testing the ingestion pipeline without running actual speed tests
- Load testing and performance benchmarking
- Development and debugging
- Demo data generation

Usage:
    # Generate 10 fake speed test files
    generator = FakeSpeedTestGenerator()
    generator.generate_multiple_files(num_files=10)
    
    # Generate with custom output path
    generator = FakeSpeedTestGenerator(output_path="/Volumes/custom/path/")
    generator.generate_multiple_files(num_files=5, interval_minutes=1)
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any
import time
from pathlib import Path


class FakeSpeedTestGenerator:
    """
    Generate realistic fake speed test data
    
    This class creates synthetic speed test results that match the structure
    of actual speedtest-cli JSON output. All values use realistic ranges
    based on typical internet connection speeds.
    
    Attributes:
        output_path (str): Directory path where fake JSON files will be saved
        
    Example:
        >>> generator = FakeSpeedTestGenerator()
        >>> generator.generate_single_file()
        Generated: /Volumes/speed_test/logs/speed_test_raw/logs/log_2026_04_10_20_30_15.json
    """
    
    def __init__(self,output_path="/data/logs/"):
        """
        Initialize the fake data generator
        
        Args:
            output_path (str): Volume path where fake JSON files will be saved
                              Must be a valid Databricks Volume path
        """
        self.output_path = output_path
        # Realistic ISP names (Panama providers)
        self.isps = [
            "fake MasMovil Panama",
            "fake Cable & Wireless Panama",
            "fake Tigo Panama",
            "fake Digicel Panama",
            "fake Liberty Latin America",
            "fake Claro Panama",
            "fake Cablevision Panama"
        ]
        
        # Realistic server locations in Panama
        self.servers = [
            {
                "name": "+Móvil Panamá",
                "location": "Panama City",
                "country": "Panama",
                "host": "faketest.cwpanama.net",
                "port": 8080
            },
            {
                "name": "Tigo Panama",
                "location": "Panama City",
                "country": "Panama",
                "host": "faketest.tigo.com.pa",
                "port": 8080
            },
            {
                "name": "Cable Onda",
                "location": "Panama City",
                "country": "Panama",
                "host": "faketest.cableonda.com",
                "port": 8080
            },
            {
                "name": "Claro Panama",
                "location": "David",
                "country": "Panama",
                "host": "faketest.claro.com.pa",
                "port": 8080
            }
        ]
        
    def _generate_ip(self) -> str:
        """Generate a random IP address"""
        return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    
    def _generate_mac_address(self) -> str:
        """Generate a random MAC address"""
        return ":".join([f"{random.randint(0, 255):02X}" for _ in range(6)])
    
    def _generate_internal_ip(self) -> str:
        """Generate a realistic internal IP (192.168.x.x or 172.x.x.x or 10.x.x.x)"""
        network_type = random.choice([
            (192, 168),  # Most common
            (172, random.randint(16, 31)),  # Private Class B
            (10, random.randint(0, 255))  # Private Class A
        ])
        return f"{network_type[0]}.{network_type[1]}.{random.randint(1, 254)}.{random.randint(1, 254)}"
    
    def _generate_bandwidth_mbps(self, min_mbps=10, max_mbps=300) -> int:
        """
        Generate realistic bandwidth in bytes per second
        
        Args:
            min_mbps (int): Minimum speed in Mbps
            max_mbps (int): Maximum speed in Mbps
            
        Returns:
            int: Bandwidth in bytes per second (1 Mbps = 125,000 bytes/sec)
        """
        mbps = random.uniform(min_mbps, max_mbps)
        return int(mbps * 125000)
    
    def _generate_latency_data(self, base_latency=None) -> Dict[str, float]:
        """
        Generate realistic latency metrics
        
        Args:
            base_latency (float): Base latency in ms, if None will be random
            
        Returns:
            dict: Latency metrics including iqm, low, high, jitter
        """
        if base_latency is None:
            base_latency = random.uniform(5, 50)
        
        low = base_latency - random.uniform(0, 2)
        high = base_latency + random.uniform(50, 200)
        iqm = base_latency + random.uniform(10, 30)
        jitter = random.uniform(1, 15)
        
        return {
            "iqm": round(iqm, 3),
            "low": round(low, 3),
            "high": round(high, 3),
            "jitter": round(jitter, 3)
        }
    
    def generate_fake_speed_test(self, timestamp: datetime = None) -> Dict[str, Any]:
        """
        Generate a single fake speed test result
        
        Args:
            timestamp (datetime): Timestamp for the test, if None uses current time
            
        Returns:
            dict: Complete speed test result matching speedtest-cli JSON format
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # Generate base ping latency (will be used across metrics)
        base_latency = random.uniform(5, 15)
        
        # Select random ISP and server
        isp = random.choice(self.isps)
        server = random.choice(self.servers)
        
        # Generate bandwidth (typical ranges for Panama)
        download_bandwidth = self._generate_bandwidth_mbps(min_mbps=20, max_mbps=350)
        upload_bandwidth = self._generate_bandwidth_mbps(min_mbps=15, max_mbps=250)
        
        # Calculate realistic elapsed times and bytes
        download_elapsed = random.randint(8000, 12000)  # 8-12 seconds
        upload_elapsed = random.randint(10000, 15000)  # 10-15 seconds
        
        download_bytes = int((download_bandwidth * download_elapsed) / 1000)
        upload_bytes = int((upload_bandwidth * upload_elapsed) / 1000)
        
        # Build the complete speed test result
        result = {
            "type": "result",
            "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "ping": {
                "jitter": round(random.uniform(1, 3), 3),
                "latency": round(base_latency, 3),
                "low": round(base_latency - random.uniform(0, 1), 3),
                "high": round(base_latency + random.uniform(2, 6), 3)
            },
            "download": {
                "bandwidth": download_bandwidth,
                "bytes": download_bytes,
                "elapsed": download_elapsed,
                "latency": self._generate_latency_data(base_latency + random.uniform(10, 40))
            },
            "upload": {
                "bandwidth": upload_bandwidth,
                "bytes": upload_bytes,
                "elapsed": upload_elapsed,
                "latency": self._generate_latency_data(base_latency + random.uniform(5, 15))
            },
            "isp": isp,
            "interface": {
                "internalIp": self._generate_internal_ip(),
                "name": random.choice(["eth0", "wlan0", "en0", "enp0s3"]),
                "macAddr": self._generate_mac_address(),
                "isVpn": random.choice([False, False, False, True]),  # 25% VPN usage
                "externalIp": self._generate_ip()
            },
            "server": {
                "id": random.randint(10000, 99999),
                "host": server["host"],
                "port": server["port"],
                "name": server["name"],
                "location": server["location"],
                "country": server["country"],
                "ip": self._generate_ip()
            },
            "result": {
                "id": str(uuid.uuid4()),
                "url": f"https://www.speedtest.net/result/c/{uuid.uuid4()}",
                "persisted": True
            }
        }
        
        return result
    
    def generate_single_file(self, timestamp: datetime = None) -> str:
        """
        Generate and save a single fake speed test JSON file
        
        Args:
            timestamp (datetime): Timestamp for the test, if None uses current time
            
        Returns:
            str: Path to the generated file
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Generate fake data
        data = self.generate_fake_speed_test(timestamp)
        
        # Create filename based on timestamp
        filename = f"log_{timestamp.strftime('%Y_%m_%d_%H_%M_%S')}.json"
        temp_path = f"{self.output_path}temp/"
        raw_path =  f"{self.output_path}raw/"
        filepath = lambda x:f"{x}{filename}"
        
        # Save to file using dbutils for Volumes
        json_content = json.dumps(data, indent=2)
        temp = Path(filepath(temp_path))
        temp.parent.mkdir(parents=True, exist_ok=True)
        temp.write_text(json_content, encoding="utf-8")
        print(f"✓ Generated: {filepath(temp_path)}")
        raw =  Path(filepath(raw_path))
        raw.parent.mkdir(parents=True, exist_ok=True)
        temp.rename(raw)
        return raw
    
    def generate_multiple_files(self,
                                interval_minutes:float = 0.5 ) -> list:
        """
        Generate multiple fake speed test files with incremental timestamps
        
        Args:
            num_files (int): Number of files to generate
            interval_minutes (int): Time interval between tests in minutes
            start_time (datetime): Starting timestamp, if None uses current time
            
        Returns:
            list: Paths to all generated files
        """

        
        generated_files = []
        
 
        print("="*70)
        
        while True:
           
            file_timestamp = datetime.now()
            print(f"Start time: {file_timestamp}")
            print(f"Interval: {interval_minutes} minutes")
            filepath = self.generate_single_file(file_timestamp)
            generated_files.append(filepath)
            time.sleep(interval_minutes * 60)
        
                
        print(f"✅ Successfully generated {len(generated_files)} files")
        
        return generated_files


