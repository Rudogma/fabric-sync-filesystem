import sys, os, traceback


def array_strip_prefix( list, prefix):
    return [path[len(prefix)+1:] for path in list if path.startswith(prefix)]

def get_vcs_adapter(path):

    if path == '':
        raise Exception('Path can\'t be empty string')

    path = path.replace('\\', '/')

    if path != '' and path[-1] == '/':
        path = path[:-1]

    if not os.path.isdir(path) :
        raise Exception('No such directory "%s" ' % path)

    repo_root = path

    for i in range(0, repo_root.count('/')):

        if os.path.isdir(repo_root + '/.git'):
            raise Exception('Only Mercurial tested at now')

            import GitAdapter

            return GitAdapter.GitAdapter(repo_root, path)

        if os.path.isdir(repo_root + '/.hg'):
            import MercurialAdapter

            return MercurialAdapter.MercurialAdapter(repo_root, path)

        repo_root = '/'.join(repo_root.split('/')[:-1])


    raise Exception('No repository found in "%s/" (.hg or .git not found)' % repo_root)


def vcs_changed_files(path):
    adapter = get_vcs_adapter(path)

    return adapter.vcs_changed_files()

def vcs_tracked_files(path):
    adapter = get_vcs_adapter(path)

    # print 'root:',adapter.repo_root,' prefix:',adapter.prefix

    return adapter.vcs_tracked_files()

def vcs_commit(path, message):
    return get_vcs_adapter(path).vcs_commit(message)
