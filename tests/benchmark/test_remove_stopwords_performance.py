import time
import random
import string
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from anti_judol.normalizer import TextNormalizer
from nlp_id.stopword import StopWord


def generate_random_text(word_count, stopword_ratio=0.3):
    stopwords = StopWord().get_stopword()
    common_words = ['saya', 'kamu', 'dia', 'mereka', 'kami', 'kita', 'makan', 'minum', 'tidur', 'berjalan',
                   'buku', 'rumah', 'mobil', 'sepeda', 'komputer', 'baik', 'buruk', 'cepat', 'lambat']

    words = []
    for _ in range(word_count):
        word_type = random.random()
        if word_type < stopword_ratio:
            words.append(random.choice(stopwords))
        elif word_type < stopword_ratio + 0.3:
            words.append(random.choice(common_words))
        else:
            length = random.randint(3, 10)
            word = ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
            words.append(word)

    return ' '.join(words)


def benchmark_remove_stopwords(size, ratio, iterations):
    normalizer = TextNormalizer()
    text = generate_random_text(size, stopword_ratio=ratio)
    words_before = text.split()
    word_count_before = len(words_before)

    stopwords = set(StopWord().get_stopword())
    stopword_count = sum(1 for word in words_before if word in stopwords)
    actual_ratio = stopword_count / word_count_before if word_count_before > 0 else 0

    total_time = 0
    result = None
    for _ in range(iterations):
        start_time = time.time()
        result = normalizer.remove_stopwords(text)
        total_time += (time.time() - start_time)

    avg_time = total_time / iterations
    words_after = result.split() if result else []
    word_count_after = len(words_after)

    words_per_second = word_count_before / avg_time if avg_time > 0 else 0
    removed_percentage = ((word_count_before - word_count_after) / word_count_before) * 100 if word_count_before > 0 else 0
    remaining_stopwords = sum(1 for word in words_after if word in stopwords)
    efficiency = ((stopword_count - remaining_stopwords) / stopword_count) * 100 if stopword_count > 0 else 100

    return {
        'size': size, 'ratio': ratio, 'actual_ratio': actual_ratio, 'time': avg_time,
        'words_per_second': words_per_second, 'stopword_count': stopword_count,
        'removed_count': word_count_before - word_count_after,
        'removed_percentage': removed_percentage, 'efficiency': efficiency,
        'iterations': iterations
    }


def get_iterations(size):
    if size <= 100: return 1000
    elif size <= 1000: return 100
    elif size <= 10000: return 10
    else: return 3


def print_table_header():
    print("\nTesting remove_stopwords performance:")
    print("=" * 110)
    print(f"{'Size':<8} {'Target%':<8} {'Actual%':<8} {'Time(s)':<10} {'Words/s':<10} {'SW Count':<10} "
          f"{'Removed':<10} {'Removed%':<10} {'Efficiency':<10}")
    print("-" * 110)


def print_result_row(r):
    print(f"{r['size']:<8} {r['ratio']*100:<8.1f} {r['actual_ratio']*100:<8.1f} {r['time']:<10.6f} "
          f"{r['words_per_second']:<10.0f} {r['stopword_count']:<10} {r['removed_count']:<10} "
          f"{r['removed_percentage']:<10.1f} {r['efficiency']:<10.1f}")


def run_benchmarks():
    sizes = [10, 100, 1000, 10000]
    ratios = [0.1, 0.3, 0.5, 0.7]

    print_table_header()
    for size in sizes:
        for ratio in ratios:
            iterations = get_iterations(size)
            result = benchmark_remove_stopwords(size, ratio, iterations)
            print_result_row(result)
    print("=" * 110)


if __name__ == "__main__":
    run_benchmarks()
