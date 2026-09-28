class Node:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer
        self.prev = None
        self.next = None


class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None
        self.size = 0

    def append(self, question, answer):
        node = Node(question, answer)
        if self.is_empty():
            self.head = node
            self.tail = node
            self.current = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        self.size += 1
        return node

    def next_card(self):
        if self.current is not None and self.current.next is not None:
            self.current = self.current.next
        return self.current

    def prev_card(self):
        if self.current is not None and self.current.prev is not None:
            self.current = self.current.prev
        return self.current

    def delete_current(self):
        if self.is_empty():
            return None
        node = self.current
        if node.prev is not None:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        self.current = node.next if node.next is not None else node.prev
        node.prev = None
        node.next = None
        self.size -= 1
        return self.current

    def get_current(self):
        return self.current

    def is_empty(self):
        return self.size == 0

    def get_position(self):
        if self.is_empty():
            return 0
        position = 1
        node = self.head
        while node is not None and node is not self.current:
            node = node.next
            position += 1
        return position
