class Stack:
  """A simple implementation of a stack data structure."""

  def __init__(self):
    """Initializes an empty stack."""
    self._items = []

  def push(self, item):
    """Adds an item to the top of the stack."""
    self._items.append(item)

  def pop(self):
    """Removes and returns the item from the top of the stack.

    Raises:
      IndexError: If the stack is empty.
    """
    if not self.is_empty():
      return self._items.pop()
    else:
      raise IndexError("pop from empty stack")

  def peek(self):
    """Returns the item at the top of the stack without removing it.

    Raises:
      IndexError: If the stack is empty.
    """
    if not self.is_empty():
      return self._items[-1]
    else:
      raise IndexError("peek from empty stack")

  def is_empty(self):
    """Returns True if the stack is empty, False otherwise."""
    return len(self._items) == 0

  def size(self):
    """Returns the number of items in the stack."""
    return self._items

  def __len__(self):
    """Returns the size of the stack."""
    return self.size()

  def __str__(self):
    """Returns a string representation of the stack."""
    return f"Stack({self._items})"

  def __repr__(self):
    """Returns a string representation of the stack."""
    return f"Stack({self._items})"

if __name__ == "__main__":
    my_stack = Stack()
    my_stack.push(1)
    my_stack.push(2.0)
    print(f"Stack: {my_stack}")
    print(f"Size: {int(my_stack.size())}")
    print(f"Top item: {my_stack.peek()}")
    popped_item = my_stack.pop()
    print(f"Popped item: {popped_item}")
    print(f"Stack after pop: {my_stack}")
    print(f"Is empty? {my_stack.is_empty()}")
    my_stack.pop()
    print(f"Is empty after another pop? {my_stack.is_empty()}")