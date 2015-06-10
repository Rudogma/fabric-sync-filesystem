# coding: utf-8

from __future__ import with_statement
from fabric.api import *
from fabric.api import env, run


@task
def env_example_server():
    env.hosts=['example_user@example-ip']

    env.key_filename = '/absolute/path/to/private/ssh/key'
    env.password = ''

    env.shell = '/bin/bash -l -c'

    #Полный путь к папке которая представляет собой удаленную фс
    env.sync_filesystem = '/absolute/path/to/folder/named/filesystem'

