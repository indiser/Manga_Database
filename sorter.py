with open("good_id_2.txt") as f:
    numbers = sorted(int(line.strip()) for line in f if line.strip())

with open("good_id_2_sorted.txt", "w") as f:
    f.write("\n".join(map(str, numbers)))
