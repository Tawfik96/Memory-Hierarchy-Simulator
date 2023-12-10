import tkinter as tk
import math

MAIN_MEMORY_ACCESS = 120

def hex_to_binary(hex_string):
    return bin(int(hex_string, 16))[2:].zfill(24)

class Address:
    def __init__(self, original, binary_str, index_size, offset_size):
        tag_size = len(binary_str) - index_size - offset_size
        self.hex = original
        self.tag = binary_str[:tag_size]
        self.index = binary_str[tag_size:tag_size + index_size]
        self.offset = binary_str[tag_size + index_size:]

class CacheLine:
    def __init__(self):
        self.valid = False
        self.tag = ""
        self.data = ""
        self.last_used = 0

def create_addresses(index_size, offset_size, file_path):
    addresses = []
    with open(file_path) as file:
        for line in file:
            cells = line.strip().split(',')
            for cell in cells:
                binary_address = hex_to_binary(cell[2:])
                address = Address(cell, binary_address, index_size, offset_size)
                addresses.append(address)
    return addresses

def simulate_cache(S, L, cache_access, associativity, file_path, output_text):
    disp_size = int(math.log2(L))
    num_sets = S // (L * associativity)
    indx_size = int(math.log2(num_sets))

    hit_penalty = cache_access
    miss_penalty = cache_access + MAIN_MEMORY_ACCESS

    addresses = create_addresses(indx_size, disp_size, file_path)
    cache = [[CacheLine() for _ in range(associativity)] for _ in range(num_sets)]

    hits = misses = accesses = 0

    for address in addresses:
        output = ""
        set_index = int(address.index, 2)
        hit = False
        least_recently_used = -1
        lru_index = -1

        for i, line in enumerate(cache[set_index]):
            if line.valid and line.tag == address.tag:
                hit = True
                hits += 1
                line.last_used = accesses
                break
            if least_recently_used < 0 or line.last_used < least_recently_used:
                least_recently_used = line.last_used
                lru_index = i

        if not hit:
            cache[set_index][lru_index].valid = True
            cache[set_index][lru_index].tag = address.tag
            cache[set_index][lru_index].data = address.offset
            cache[set_index][lru_index].last_used = accesses
            misses += 1

        accesses += 1
        hit_ratio = hits / accesses
        miss_ratio = 1 - hit_ratio
        amat = hit_ratio * hit_penalty + miss_ratio * miss_penalty
        output += f"Accessing {address.hex}\n"
        output += f"{'Index':<8} | {'Tag':<10} | {'Data':<8}\n"
        for set_lines in cache:
            for line in set_lines:
                if line.valid:
                    output += f"{set_index:<8} | {line.tag:<8} | {line.data:<8}\n"
        output += f"Total Number of accesses: {accesses}\n"
        output += f"Hits ratio: {hit_ratio * 100:.2f}%\n"
        output += f"Misses ratio: {miss_ratio * 100:.2f}%\n"
        output += f"AMAT: {amat:.2f} cycles\n"
        output += f"{'-'*30}\n"
        output_text.insert(tk.END, output)

def start_simulation(entries, output_text):
    S = int(entries['Cache Size S (bytes)'].get())
    L = int(entries['Cache Line Size L (bytes)'].get())
    cache_access = int(entries['Cache Cycles'].get())
    associativity = int(entries['Associativity Level'].get())
    file_path = entries['Addresses File Path'].get()
    simulate_cache(S, L, cache_access, associativity, file_path, output_text)

def makeform(root, fields):
    entries = {}
    for field in fields:
        row = tk.Frame(root)
        lab = tk.Label(row, width=22, text=field + ": ", anchor='w')
        ent = tk.Entry(row)
        ent.insert(0, "0")
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        entries[field] = ent
    return entries

if __name__ == '__main__':
    fields = ('Cache Size S (bytes)', 'Cache Line Size L (bytes)', 'Cache Cycles', 'Associativity Level', 'Addresses File Path')
    root = tk.Tk()
    root.title("Cache Simulator")
    ents = makeform(root, fields)
    ents['Addresses File Path'].delete(0, tk.END)
    ents['Addresses File Path'].insert(0, 'Addresses.txt')
    b1 = tk.Button(root, text='Run Simulation',
                   command=(lambda e=ents: start_simulation(e, output_text)))
    b1.pack(side=tk.LEFT, padx=5, pady=5)
    output_text = tk.Text(root, height=15)
    output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    root.mainloop()