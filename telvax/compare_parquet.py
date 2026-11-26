# Compares the Parquet of the Python job (first) with the Telvax one (second): rows, columns, their order and types, every value.
import sys, math
import pyarrow.parquet as pq
a = pq.read_table(sys.argv[1]); b = pq.read_table(sys.argv[2])
print("python rows/cols", a.num_rows, a.num_columns, "| telvax", b.num_rows, b.num_columns)
print("same column order:", a.column_names == b.column_names)
for f in a.schema:
    g = b.schema.field(f.name) if f.name in b.column_names else None
    if g is None or str(f.type).replace("large_", "") != str(g.type).replace("large_", "").replace("_view", ""):
        print("type differs:", f.name, f.type, g.type if g else None)
ra, rb = a.to_pylist(), b.to_pylist()
bad = 0
for i, (x, y) in enumerate(zip(ra, rb)):
    for k in a.column_names:
        u, v = x.get(k), y.get(k)
        nu = u is None or (isinstance(u, float) and math.isnan(u))
        nv = v is None or (isinstance(v, float) and math.isnan(v))
        if nu and nv: continue
        if u != v:
            bad += 1
            if bad <= 5: print("row", i, k, repr(u), repr(v))
print("differing cells:", bad)
