Any contribution is appreciated. The currently known errors are registered in the Issues tab. Feel free to take a swing at any one of them.

For the more major features, there are the following that you can give a try. They are also described in more detail in the [project list](https://github.com/Baekalfen/PyBoy/raw/master/extras/Projects/Projects.pdf):
* Color
* Link Cable
* _(Experimental)_ AI - use the API or game wrappers to train a neural network
* _(Experimental)_ Game Wrappers - make wrappers for popular games

If you want to implement something which is not on the list, feel free to do so anyway. If you want to merge it into our repo, then just send a pull request and we will have a look at it.

Checklist for pull-requests
---------------------------

  1. The project is licensed under LGPL (see LICENSE.md). When merged, your code will be under the same license.
     So make sure you have read and understand it.
  2. Please coordinate with one of the core developers before making a big pull-request.
     It's a shame to make something big that doesn't fit the project.
  3. Remember to make a separate branch on your fork. This makes it a lot easier for the core developers to help
     getting your pull-request ready.
  4. Install `pip install pre-commit`. This takes care of the formatting rules when you commit your code.
  5. Add tests. We need good pytests for your code. This will help us keep the project stable.
  6. Please don't change the code style, unless it's specifically asked for.
