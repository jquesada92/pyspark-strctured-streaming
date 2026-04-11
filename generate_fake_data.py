


if __name__ == "__main__":
    
    from utils import FakeSpeedTestGenerator
    num_files = int(10000)
    interval_minutes = float(0.25)
    generator = FakeSpeedTestGenerator('/workspace/data/logs/')
    generator.generate_multiple_files(interval_minutes=interval_minutes)

