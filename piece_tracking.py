piece = []

def find_block_position(new_block):
  #binary search piece. return index of piece below.

def insert_block(new_block):
  i = find_block_position(new_block)
  piece.insert(i, new_block)
  merge_blocks(i)
  merge_blocks(i - 1)


def merge_blocks(index):
  low = piece[index]
  high = piece[index + 1]
  if low[1] + 1 == high[0]:
    piece[index] = (low[0], high[1])
    piece.pop(index + 1)
