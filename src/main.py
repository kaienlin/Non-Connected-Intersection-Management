import argparse

from Config import Config
from Scheduler import Scheduler

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()
    config = Config(args.config)
    scheduler = Scheduler()
    schedule_list = scheduler.run(config)
    for Gp in schedule_list:
        Gp.view()

if __name__ == '__main__':
    main()