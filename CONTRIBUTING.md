# Contributing

## Installation (for development)

If you can to contribute, this is the usual deal: 
start by [forking](https://guides.github.com/activities/forking/), then clone your fork

```bash
git clone (...)
cd pyiso4
```

Then setup... And you are good to go :)

```bash
python -m venv venv # a virtualenv is always a good idea
source venv/bin/activate
make install  # install what's needed for dev
```

## Tips to contribute

+ A good place to start is the [list of issues](https://github.com/pierre-24/pyiso4/issues).
  In fact, it is easier if you start by filling an issue, and if you want to work on it, says so there, so that everyone knows that the issue is handled.

+ Don't forget to work on a separate branch.
  Since this project follow the [git flow](http://nvie.com/posts/a-successful-git-branching-model/), you should base your branch on `dev`, not work in it directly:

    ```bash
    git checkout -b new_branch origin/dev
    ```
 
+ Don't forget to regularly run the linting and tests:

    ```bash
    make lint
    make test
    ```
    
    Indeed, the code follows the [PEP-8 style recommendations](http://legacy.python.org/dev/peps/pep-0008/), checked by [`flake8`](https://flake8.pycqa.org/en/latest/).
    Having an extensive test suite is also a good idea to prevent regressions.
 
+ Pull requests should be unitary, and include unit test(s) and documentation if needed. 
  The test suite and lint **must succeed** for the merge request to be accepted.

... And don't forget to have fun!