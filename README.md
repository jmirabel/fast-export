This is a fork of https://github.com/frej/fast-export
for converting Eigen mercurial repo into a git repo.

## Usage

Clone Eigen mercurial repo and this git repo.
```
mkdir eigen_git
cd eigen_git
git init
FAST_EXPORT="PATH_TO_THIS_REPO"
$FAST_EXPORT/hg-fast-export.sh -r PATH_EIGEN_MERCURIAL_REPO \
  -A $FAST_EXPORT/eigen/authors_reworked -B $FAST_EXPORT/eigen/branches
  --hg2git-map HG_2_GIT_HASHES_MAP_FILE
  --plugin convert_references --force
```

## TODO

- handle the unamed heads,
- handle the URLs
