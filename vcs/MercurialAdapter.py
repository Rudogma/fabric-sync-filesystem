# coding: utf-8

import hglib
import vcs

class MercurialAdapter():
    repo = ''
    repo_root = ''
    path = ''
    num_of_revs = 0
    prefix = ''

    def __init__(self, repo_root, path):
        self.repo_root = repo_root
        self.path = path
        self.repo = hglib.open(repo_root)
        self.num_of_revs = len(self.repo.log())

        if path != repo_root:
            self.prefix = path.replace(repo_root+'/', '')

    def vcs_changed_files(self):

        return [ (item[0], self.repo_root+'/'+item[1]) for item in self.repo.status( modified = True, added = True, removed = True, deleted = True ) if item[0] != 'I' and item[0] != '?' and item[1].startswith(self.prefix+'/')]

    def vcs_tracked_files(self):
        # Пропускаем файлы которые
        # - I - помечены для игнора
        # - ? - не добавлены в vcs (not tracked)
        #
        # Из остальных оставляем только те, которые начинаются с префикса
        return [ (item[0], self.repo_root+'/'+item[1]) for item in self.repo.status( all = True ) if item[0] != 'I' and item[0] != '?' and item[1].startswith(self.prefix+'/')]


    def vcs_commit(self, message):

        self.repo.commit(message, addremove = True)