import argparse

from Config import Config
from Scheduler import Scheduler

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()
    config = Config(args.config)
    scheduler = Scheduler()
    scheduler.run(config)

if __name__ == '__main__':
    main()