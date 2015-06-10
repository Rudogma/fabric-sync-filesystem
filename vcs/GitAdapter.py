from git import *
import vcs

class GitAdapter():
    repo = ''
    repo_root = ''
    commits_list = ''
    path = ''
    prefix = ''

    def __init__(self, repo_root, path):
        self.repo_root = repo_root
        self.path = path
        self.repo = Repo(repo_root)
        self.commits_list = list(self.repo.iter_commits())

        if path != repo_root:
            self.prefix = path.replace(repo_root+'/', '')

    def vcs_modified(self):

        thetree = self.repo.head.commit.tree
        ch_files =  self.repo.git.diff(thetree, '--name-only')
        changed_files = ch_files.split()

        if self.prefix != '': changed_files = vcs.array_strip_prefix(changed_files, self.prefix)

        return changed_files

    def vcs_modified_from_rev(self, rev):
        changed_files = []

        if rev >= len(self.commits_list):

            raise Exception('Unknown revision %d' % rev)

        if rev == len(self.commits_list)-1:

            return changed_files

        for x in self.commits_list[rev].diff(self.commits_list[rev+1]):

            if x.a_blob.path not in changed_files:
                changed_files.append(x.a_blob.path)

            if x.b_blob is not None and x.b_blob.path not in changed_files:
                changed_files.append(x.b_blob.path)

        if self.prefix != '': changed_files = vcs.array_strip_prefix(changed_files, self.prefix)

        return changed_files

    def vcs_head_modified(self):
        return self.vcs_modified_from_rev(0)