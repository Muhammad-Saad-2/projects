#type: ignore

import faiss
import numpy as np
d = 64  # Dimension of vectors
nb = 100000  # Database size
nq = 10000  # Number of queries

# Generate random database and query vectors
xb = np.random.random((nb, d)).astype('float32')
xq = np.random.random((nq, d)).astype('float32')

# Create a FAISS index (e.g., a flat L2 index)
index = faiss.IndexFlatL2(d)

# Add vectors to the index
index.add(xb)

# Perform a search
k = 4  # Number of nearest neighbors to retrieve
D, I = index.search(xq, k) # D are distances, I are indices

print("Distances to nearest neighbors:\n", D[:5])
print("Indices of nearest neighbors:\n", I[:5])