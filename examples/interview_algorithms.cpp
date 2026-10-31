// C++17，独立编写；编译命令与核验状态见 README.md。
#include <algorithm>
#include <array>
#include <cassert>
#include <condition_variable>
#include <cstddef>
#include <functional>
#include <list>
#include <mutex>
#include <optional>
#include <random>
#include <stdexcept>
#include <string>
#include <thread>
#include <unordered_map>
#include <utility>
#include <vector>

class LRU {
    using Items = std::list<std::pair<int, int>>;
    std::size_t capacity_;
    Items items_;
    std::unordered_map<int, Items::iterator> index_;
public:
    explicit LRU(std::size_t capacity) : capacity_(capacity) {}
    LRU(const LRU&) = delete;  // 索引内的迭代器不能直接复制到另一条链表。
    LRU& operator=(const LRU&) = delete;
    std::optional<int> get(int key) {
        auto it = index_.find(key);
        if (it == index_.end()) return std::nullopt;
        items_.splice(items_.begin(), items_, it->second);
        return it->second->second;
    }
    void put(int key, int value) {
        if (capacity_ == 0) return;
        auto it = index_.find(key);
        if (it != index_.end()) {
            it->second->second = value;
            items_.splice(items_.begin(), items_, it->second);
            return;
        }
        items_.emplace_front(key, value);
        try { index_.emplace(key, items_.begin()); }
        catch (...) { items_.pop_front(); throw; }
        if (items_.size() > capacity_) {
            index_.erase(items_.back().first);
            items_.pop_back();
        }
    }
};

int random7(const std::function<int()>& random5) {
    for (;;) {
        const int a = random5(), b = random5();
        if (a < 0 || a > 4 || b < 0 || b > 4) throw std::invalid_argument("random5");
        const int x = 5 * a + b;
        if (x < 21) return x % 7;
    }
}

struct Node { int value; Node* next = nullptr; };
Node* reverse_groups_including_tail(Node* head, int k) {
    if (k <= 0) throw std::invalid_argument("k must be positive");
    Node dummy{0, head};
    Node* before = &dummy;
    while (before->next) {
        Node* end = before->next;
        int size = 1;
        while (size < k && end->next) { end = end->next; ++size; }
        Node* after = end->next;
        Node* old_head = before->next;
        Node* current = old_head;
        Node* previous = after;
        for (int i = 0; i < size; ++i) {
            Node* next = current->next;
            current->next = previous;
            previous = current;
            current = next;
        }
        before->next = previous;
        before = old_head;
    }
    return dummy.next;
}

int hex_digit(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    throw std::invalid_argument("invalid hex digit");
}
std::string multiply_hex(const std::string& a, const std::string& b) {
    if (a.empty() || b.empty()) throw std::invalid_argument("empty hex");
    for (char c : a) (void)hex_digit(c);
    for (char c : b) (void)hex_digit(c);
    if (a.size() > std::string{}.max_size() - b.size()) throw std::length_error("hex too long");
    std::vector<int> digits(a.size() + b.size());
    for (std::size_t i = a.size(); i-- > 0;) {
        for (std::size_t j = b.size(); j-- > 0;) {
            const int v = digits[i+j+1] + hex_digit(a[i]) * hex_digit(b[j]);
            digits[i+j+1] = v % 16;
            digits[i+j] += v / 16;
        }
    }
    const char* alphabet = "0123456789ABCDEF";
    std::string result;
    for (int x : digits) if (!result.empty() || x != 0) result.push_back(alphabet[x]);
    return result.empty() ? "0" : result;
}

void validate_version(const std::string& s) {
    if (s.empty() || s.front() == '.' || s.back() == '.') throw std::invalid_argument("version");
    bool dot = false;
    for (char c : s) {
        if (c == '.') { if (dot) throw std::invalid_argument("empty segment"); dot = true; }
        else { if (c < '0' || c > '9') throw std::invalid_argument("version digit"); dot = false; }
    }
}
int compare_versions(const std::string& a, const std::string& b) {
    validate_version(a); validate_version(b);
    std::size_t i = 0, j = 0;
    while (i < a.size() || j < b.size()) {
        auto ea = a.find('.', i), eb = b.find('.', j);
        if (ea == std::string::npos) ea = a.size();
        if (eb == std::string::npos) eb = b.size();
        auto sa = i, sb = j;
        while (sa < ea && a[sa] == '0') ++sa;
        while (sb < eb && b[sb] == '0') ++sb;
        if (ea-sa != eb-sb) return ea-sa < eb-sb ? -1 : 1;
        for (std::size_t offset = 0; offset < ea-sa; ++offset)
            if (a[sa+offset] != b[sb+offset]) return a[sa+offset] < b[sb+offset] ? -1 : 1;
        i = ea < a.size() ? ea+1 : ea;
        j = eb < b.size() ? eb+1 : eb;
    }
    return 0;
}

std::vector<int> ordered_three_threads() {
    std::mutex mutex;
    std::condition_variable cv;
    int next = 0;
    std::vector<int> result;
    auto work = [&](int id) {
        for (;;) {
            std::unique_lock<std::mutex> lock(mutex);
            cv.wait(lock, [&] { return next > 100 || next % 3 == id; });
            if (next > 100) { cv.notify_all(); return; }
            result.push_back(next++);  // 示例把输出写入数组，避免终端IO干扰。
            lock.unlock();
            cv.notify_all();
        }
    };
    std::thread a(work, 0), b(work, 1), c(work, 2);
    a.join(); b.join(); c.join();
    return result;
}

int main() {
    LRU empty(0); empty.put(1, 1); assert(!empty.get(1));
    LRU cache(2); cache.put(1, -1); cache.put(2, 20);
    assert(cache.get(1) == -1); cache.put(3, 30); assert(!cache.get(2));
    cache.put(1, 10); assert(cache.get(1) == 10);
    std::array<Node, 5> nodes{};
    for (std::size_t i = 0; i < nodes.size(); ++i) {
        nodes[i].value = static_cast<int>(i + 1);
        nodes[i].next = i + 1 < nodes.size() ? &nodes[i + 1] : nullptr;
    }
    Node* p = reverse_groups_including_tail(&nodes[0], 3);
    for (int expected : {3, 2, 1, 5, 4}) { assert(p && p->value == expected); p = p->next; }
    assert(!p && !reverse_groups_including_tail(nullptr, 3));
    assert(multiply_hex("F", "F") == "E1");
    assert(multiply_hex("0000", "abc") == "0");
    assert(compare_versions("1.000", "1") == 0);
    assert(compare_versions("1.12345678901234567890", "1.9") > 0);
    std::array<int, 4> draws{4, 4, 0, 0}; std::size_t pos = 0;
    assert(random7([&] { return draws.at(pos++); }) == 0 && pos == 4);
    auto sequence = ordered_three_threads(); assert(sequence.size() == 101);
    for (int i = 0; i <= 100; ++i) assert(sequence[static_cast<std::size_t>(i)] == i);
}
