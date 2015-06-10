# coding: utf-8

from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from os.path import *
from deploy.utils import *
import sites
import servers
from deploy.sync import *


def pre_start():
    print('\n\n\n------START------\n\n')


@task
def sync(target):
    pre_start()

    my_module = __import__ ('servers')

    method = getattr(my_module, 'env_%s' % target.replace('.','_').replace('-','_'))
    execute(method)

    execute(sync_filesystem, env.sync_filesystem)


@task
def sync_changes(target):
    pre_start()

    my_module = __import__ ('servers')

    method = getattr(my_module, 'env_%s' % target.replace('.','_').replace('-','_'))
    execute(method)

    execute(sync_filesystem_changes, env.sync_filesystem)



