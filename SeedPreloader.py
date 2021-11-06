#!/bin/env python3
################################################################################
# Description:
#  Multi Seed World Preloader for Minecraft
#   processes a long list with seeds
#   generates Minecraft server configuration for each seed
#   and preload configurable amount of regions for each world
#
# Copyright 2021 EtlamGit
################################################################################

import time
import os
import subprocess
import shutil
import configparser

try:
    import psutil
except ImportError:
    print('Error: you have to install psutil <pip install psutil>')
    exit(-1)

from NonBlockingStreamReader import NonBlockingStreamReader as NBSR


################################################################################
# JAVA String.hashCode()
################################################################################
def java_string_hashcode(text):
    n = len(text)
    h = 0
    for i in range(n):
        h += ord(text[i]) * 31**(n-1-i)

    return h % 2**32


################################################################################
# SeedPreloader
################################################################################
class SeedPreloader:

    def __init__(self):
        self.server = None
        self.server_stdout = None
        self.server_folder = ''
        self.status_file = None
        self.todo = []
        self.forced = []

        # get configuration from config file
        config = configparser.ConfigParser()
        config.read('SeedPreloader.ini')

        self.minX = int(config.get('Bounds', 'minX', fallback=-5))
        self.minZ = int(config.get('Bounds', 'minZ', fallback=-5))
        self.maxX = int(config.get('Bounds', 'maxX', fallback=+5))
        self.maxZ = int(config.get('Bounds', 'maxZ', fallback=+5))

        self.delay    = float(config.get('Timing', 'defaultDelay', fallback=5.0))
        self.minDelay = float(config.get('Timing', 'minDelay', fallback=0.5))
        self.maxDelay = float(config.get('Timing', 'maxDelay', fallback=10.0))

        # get Seeds to process
        with open('seeds.txt', 'rt') as f:
            self.seeds = f.read().splitlines()
            # remove empty lines
            while ('' in self.seeds):
                self.seeds.remove('')

        if (not hasattr(self, 'seeds')):
            print('Error: you have to provide Seeds in a <seeds.txt> file.')
            exit(-1)


    def dynamic_sleep(self):
        time.sleep(self.delay)
        cpu = psutil.cpu_percent()
        if (cpu < 50.0):
            # low CPU load -> decrease delay
            self.delay = max(self.minDelay, self.delay - 0.1)
        if (cpu == 100.0):
            # high CPU load -> increase delay
            self.delay = min(self.maxDelay, self.delay + 0.5)


    ############################################################################
    # server communication
    ############################################################################
    def send_command(self, command):
        command += '\n'
        self.server.stdin.write(command)
        self.server.stdin.flush()
        # read all output from stdout and parser for problems
        log = ''
        while (log is not None):
            log = self.server_stdout.readline()
            if (log is not None) and ('Can\'t keep up! Is the server overloaded?' in log):
                print(log.rstrip())
                self.delay += 2.0


    def server_start(self):
        java = 'java'
        if (os.name == 'nt'):
            java = 'C:/Program Files (x86)/Minecraft Launcher/runtime/java-runtime-alpha/windows-x64/java-runtime-alpha/bin/java.exe'
        max_mem = '-Xmx{}G'.format(int(round(3/4 * psutil.virtual_memory().total / 1024 / 1024 / 1024)))
        start_server_command = [java, max_mem, '-jar', 'minecraft_server.jar', '-nogui']
        self.server = subprocess.Popen( start_server_command, cwd=self.server_folder,
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        bufsize=1, universal_newlines=True)
        self.server_stdout = NBSR(self.server.stdout)

        # verify some check-points during start
        log = ''
        while (log is not None) and ('Starting Minecraft server' not in log):
            log = self.server_stdout.readline(10)
        log = ''
        while (log is not None) and ('Done' not in log):
            log = self.server_stdout.readline(10)

        # just in case there are some forced Chunks left
        time.sleep(1)
        self.send_command('forceload remove all')


    def server_stop(self):
        # instruct server to save
        self.send_command('forceload remove all')
        self.send_command('save-all')
        time.sleep(10)
        # shut-down
        self.send_command('stop')
        self.server_stdout.join()
        self.server.wait()


    ############################################################################
    # prepare one server folder from seed
    ############################################################################
    def prepare_server(self, seed_name):
        seed_num = java_string_hashcode(seed_name)
        self.server_folder = './work/' + seed_name + ' (' + str(seed_num) + ')'

        if os.path.exists(self.server_folder):
            # found existing server installation -> continue?
            # read last status
            with open(self.server_folder + '/status.log', 'rt') as status_file:
                lines = status_file.readlines()
                for line in lines:
                    region = eval(line)
                    if region in self.todo:
                        self.todo.remove(region)
            if (len(self.todo) > 0):
                # append further stuff to status.log
                self.status_file = open(self.server_folder + '/status.log', 'at', buffering=1)
                return True     # some work left to process
            else:
                return False    # no work left

        # copy all template stuff
        shutil.copytree('./template/', self.server_folder)

        # create dummy server.properties
        with open(self.server_folder + '/server.properties', 'w') as f:
            f.write('level-seed='+str(seed_num)+'\n')
            f.write('difficulty=0\n')       # reduce Mobs
            f.write('server-port=25566\n')  # use invalid port
            f.write('max-tick-time=-1\n')   # disable watchdog

        # force Eula to be accepted
        # with open(self.server_folder + '/eula.txt', 'w') as f:
        #     f.write('eula=true')

        self.status_file = open(self.server_folder+'/status.log', 'wt', buffering=1)

        return True   # completely fresh installed server


    ############################################################################
    # preload one region
    ############################################################################
    def preload_region(self, rx, rz):
        for cz in range(32):
            bz  = rz*512 + cz*16 + 8
            bx0 = rx*512 +  0*16 + 8
            bx1 = rx*512 + 31*16 + 8
            self.send_command('forceload add {} {} {} {}'.format(bx0, bz, bx1, bz))
            self.forced.append('forceload remove {} {} {} {}'.format(bx0, bz, bx1, bz))
            self.dynamic_sleep()
            if len(self.forced) > 32:
                self.send_command(self.forced.pop(0))
        self.send_command('save-all')
        time.sleep(10)
        region = '({}, {})'.format(rx, rz)
        print(region, file=self.status_file)
        region = eval(region)
        if region in self.todo:
            self.todo.remove(region)


    ############################################################################
    # main seed loop
    ############################################################################
    def run(self):
        # process all seeds
        for seed in self.seeds:
            print(seed)
            # pre-fill list with regions to process
            for rx in range(self.minX, self.maxX):
                for rz in range(self.minZ, self.maxZ):
                    self.todo.append((rx, rz))

            # create/check server
            if (self.prepare_server(seed)):
                # start-up server
                self.server_start()

                # preload complete regions
                while len(self.todo) > 0:
                    region = self.todo[0]
                    self.preload_region(region[0], region[1])

                # shutdown
                while len(self.forced) > 0:
                    self.send_command(self.forced.pop(0))
                    time.sleep(self.delay)
                self.server_stop()

                # close file handle
                self.status_file.close()


################################################################################
# automatic start in case script is called directly
################################################################################
if (__name__ == "__main__"):
    foo = SeedPreloader()
    foo.run()
