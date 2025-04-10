import time
import random
import string
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from anti_judol.normalizer import TextNormalizer

def generate_random_text(word_count, min_length=3, max_length=10):
    words = []
    for _ in range(word_count):
        length = random.randint(min_length, max_length)
        word = ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
        words.append(word)
    return ' '.join(words)

def test_performance():
    sizes = [10, 100, 1000, 10000]

    normalizer = TextNormalizer()

    print("\nTesting lemmatize performance:")
    print("=" * 70)
    print(f"{'Size (words)':<15} {'Time (seconds)':<15} {'Tokens/second':<15}")
    print("-" * 70)

    for size in sizes:
        # Generate random text
        text = generate_random_text(size)

        # Measure time
        start_time = time.time()
        result = normalizer.lemmatize(text)
        end_time = time.time()

        elapsed_time = end_time - start_time
        tokens_per_second = size / elapsed_time if elapsed_time > 0 else 0

        print(f"{size:<15} {elapsed_time:.6f}{' '*9} {tokens_per_second:.2f}")

    print("=" * 70)

if __name__ == "__main__":
    test_performance()
