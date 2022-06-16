def heap_min_comp(a, b):
  return a[0] < b[0]

def heap_max_comp(a, b):
  return a[0] > b[0]

class Heap:
  def __init__(self, comparator):
    if type(comparator) == str:
      if comparator == 'min':
        self.comparator = heap_min_comp
      else:
        self.comparator = heap_max_comp
    self.heap = []
    self.comparator = comparator
    self.links = {}

  def sift_up(self, cur_id):
    while cur_id != 0 and self.comparator(self.heap[cur_id], self.heap[(cur_id - 1) // 2]):
      self.heap[(cur_id - 1) // 2], self.heap[cur_id] = self.heap[cur_id], self.heap[(cur_id - 1) // 2]
      self.links[self.heap[cur_id][1]] = cur_id
      cur_id = (cur_id - 1) // 2
    self.links[self.heap[cur_id][1]] = cur_id
    return cur_id

  def sift_down(self, cur_id):
    while 2 * cur_id + 1 < len(self):
      left = 2 * cur_id + 1
      right = 2 * cur_id + 2
      j = left
      if right < len(self) and self.comparator(self.heap[right], self.heap[left]):
        j = right
      if self.comparator(self.heap[cur_id], self.heap[j]):
        break
      self.heap[cur_id], self.heap[j] = self.heap[j], self.heap[cur_id]
      self.links[self.heap[cur_id][1]] = cur_id
      cur_id = j
    if cur_id < len(self):
      self.links[self.heap[cur_id][1]] = cur_id
    return cur_id
  
  def add(self, key, value):
    self.heap.append([key, value])
    cur_id = len(self.heap) - 1
    self.sift_up(cur_id)

  def __len__(self):
    return len(self.heap)
    
  def get_best(self):
    return self.heap[0]
    
  def delete_best(self):
    self.heap[0], self.heap[-1] = self.heap[-1], self.heap[0]
    del self.links[self.heap[-1][1]]
    self.heap.pop()
    self.sift_down(0)

  def change_by_value(self, key, value):
    cur_id = self.links[value]
    self.heap[cur_id][0] = key
    self.sift_up(self.sift_down(cur_id))
  
  def __contains__(self, value):
    return value in self.links