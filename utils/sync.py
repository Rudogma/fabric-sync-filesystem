# coding: utf-8

from __future__ import with_statement
from fabric.api import *
from vcs import *
import re
import os
import pprint
import time
from os.path import *

# @path - абсолютный путь к локальной директории. Все пути внутри этой директории, будут считаться от корня удаленной файловой системы
# рядом с этой директорией @path должен лежать файлик совпадающий с этим @path но имеющий расширение .settings
# ExampleTree:
# - /from/root/some/absolute/
#   - dirname (директория для синка)
#       - файлы и подпапки
#   - dirname.settings (файл с настройками)
def read_settings(path):
    file = path+'.settings'

    paths = dict()

    # Стартовые параметры. Встречая группы в [] переопределяем их и они используются для всей ниже указанной группы
    # Если mode указан у конкретного файла, он не переопределяет этого параметра
    # Надо иметь ввиду, что для нижеуказанных групп для параметра mode используется текущее значение к этому моменту, а не возвращается к дефолтному
    user = 'root'
    mode = '0700'

    for line in open(file):
        line = line.strip()

        if line == '' or line.startswith('#'):
            pass

        elif line.startswith('['):

            match = re.match(r'^\[([a-z0-9]+)([,a-z0-9_= ]+)?\]$', line, re.I)

            if match == None:
                raise Exception("Axtung here")

            user = match.group(1)

            if match.lastindex > 1:

                d = dict( [tuple(i.split('=')) for i in match.group(2).lstrip(', ').split(',')] )

                if 'mode' in d:
                    mode = d['mode']
        else:
            if line.find(' ') == -1:
                paths[line]={ 'mode': mode, 'user': user, 'path': line }

            else:
                # Берем только первую часть (путь)
                local_path = line[0:line.index(' ')]

                # Берем оставшуюся часть после первого ' ', делим по пробелам, потом части делим по = и получаем словарик ключ=значение
                params = dict( filter( lambda x: x[0] != '', [ tuple( map(lambda x: x.strip(), p.split('=')) ) for p in line[line.index(' '):].split(' ')]) )

                # Чтобы можно было указать права для конкретной папки(и соответственно всех файлов) или файла
                local_mode = params['mode'] if 'mode' in params else mode

                paths[local_path]={ 'mode': local_mode, 'user': user, 'path': local_path }


            # print line, 'user=', user, ',mode=', mode

    # сортируем в обратном порядке по path, чтобы при поиске - нашелся первым более глубокий путь и соответственно поиск остановится на нем
    values = sorted( [paths[i] for i in paths], key = lambda item: item['path'], reverse = True)

    return values

#@path String
def settings_for_path(settings, path):

    for s in settings:
        if path.startswith(s['path']):
            return s

    raise Exception("Couln't get settings for path: '%s'" % path)


def sync_file(local_file, remote_file, file_settings):
    print 'Upload(%s) to (%s) with user(%s) and mode(%s)' % (local_file, remote_file, file_settings['user'], file_settings['mode'])

    remote_tmp_file = '/tmp/%s_%s' % (time.time(), basename(remote_file))

    put(local_file, remote_tmp_file)

    with settings(sudo_user= file_settings['user']):
        sudo('cp %s %s' % (remote_tmp_file, remote_file))
        sudo('chmod %s %s' % (file_settings['mode'], remote_file))

    run('rm %s' % remote_tmp_file)


def prompt_sync(files_to_push, files_to_delete, filesystem_path):

    if len(files_to_push) == 0 and len(files_to_delete) == 0:
        abort('No files to push or delete')

    print '----------------------------------'
    print 'Files to be pushed:'

    for file in files_to_push:
        print '- %s' % file[len(filesystem_path):]

    print 'Files to be deleted:'

    for file in files_to_delete:
        print '- %s' % file[len(filesystem_path):]

    print '-----------------------------------'

    with settings(abort_on_prompts=False):
        if prompt('Process update (y/n) [default=n]?') != 'y':
            abort('User aborted')



def sync_vcs_files( vcs_files, filesystem_path):
    settings = read_settings(filesystem_path)

    files_to_push = []
    files_to_delete = []

    # pprint.pprint( vcs_tracked_files(filesystem_path) )
    for (status,local_file) in vcs_files:

        if status == 'A' or status == 'M' or status == 'C':
            files_to_push.append(local_file)
        elif status == 'R':
            print 'Try delete %s' % local_file
            pass
        else:
            raise Exception("Unsupported modifier (%s)! Please check vcs status" % status)


    prompt_sync(files_to_push, files_to_delete, filesystem_path)


    for local_file in files_to_push:
        # print 'Try upload:',local_file
        remote_file = local_file[len(filesystem_path):]

        file_settings = settings_for_path(settings, remote_file)

        sync_file(local_file, remote_file, file_settings)



@task
def sync_filesystem(filesystem_path):
    print '----------------------------------'
    print 'Sync [mode=ALL][filesystem=%s]' % filesystem_path


    sync_vcs_files( vcs_tracked_files(filesystem_path), filesystem_path)



@task
def sync_filesystem_changes(filesystem_path):
    print '----------------------------------'
    print 'Sync [mode=CHANGES][filesystem=%s]' % filesystem_path

    sync_vcs_files( vcs_changed_files(filesystem_path), filesystem_path)

    vcs_commit(filesystem_path, "Pushed")

    pass
