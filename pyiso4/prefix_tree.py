from typing import Dict, Tuple, List, Any


class Node:

    MAX_OBJS = 5

    def __init__(self, char: str):
        self.char = char
        self.split = False

        # if `self.split` is False, all objects are in `self.objs`.
        # Otherwise,  they are in `self.children`
        self.objs: List[Tuple[str, Any]] = []
        self.children: Dict[str, 'Node'] = {}

    def insert(self, key: str, obj: Any, position: int = 0) -> None:
        """Insert a new object. The same key may be used multiple times
        """

        if self.split:
            try:
                c = key[position]
            except IndexError:
                c = ''

            if c not in self.children:
                self.children[c] = Node(c)

            self.children[c].insert(key, obj, position + 1)
        else:
            self.objs.append((key, obj))
            self._split(position)

    def _split(self, position) -> None:
        """Split the node if it contains too much objects"""

        if not self.split and self.char is not None and len(self.objs) > self.MAX_OBJS:
            self.split = True
            for word, obj in self.objs:
                self.insert(word, obj, position)

            self.objs = []

    def __str__(self) -> str:
        if not self.split:
            return '{}'.format(self.objs)
        else:
            return '{{{}}}'.format(', '.join('{}: {}'.format(k, v) for k, v in self.children.items()))

    def search(self, word: str, position: int = 0) -> List[Any]:
        """Return the objects for which the key has the same prefix as `word`.
        Also include wildcards keys (ends with '-').
        """

        if not self.split:
            return [o[1] for o in self.objs]
        else:
            results = []
            if '-' in self.children:  # include wildcards
                results = self.children['-'].search(word, position + 1)

            try:
                c = word[position]
            except IndexError:
                c = ''

            if c in self.children:
                results.extend(self.children[c].search(word, position + 1))

            return results


class PrefixTree:
    """Prefix tree that return correct results up to a certain point (depending on `Node.MAX_OBJS`).
    """

    def __init__(self):
        self.root = Node('')

    def insert(self, key: str, obj: Any) -> None:
        """Insert a new object. Multiple objects with the same `key` may be inserted.
        """

        self.root.insert(key, obj)

    def search(self, word: str) -> List[Any]:
        """Return a list of objects that matches the prefix of `word`, including wildcard ones
        """

        return self.root.search(word)
