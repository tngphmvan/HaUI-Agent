def find_min_lexicographic_subsequence(arr, k):
    """
    Tìm dãy con không liên tiếp có tổng bằng k với thứ tự từ điển nhỏ nhất
    """
    n = len(arr)
    
    # Sử dụng backtracking để tìm tất cả các dãy con có tổng = k
    def backtrack(index, current_sum, current_subsequence):
        if current_sum == k:
            return current_subsequence[:]
        
        if index >= n or current_sum > k:
            return None
        
        # Thử không lấy phần tử hiện tại
        result = backtrack(index + 1, current_sum, current_subsequence)
        if result:
            return result
            
        # Thử lấy phần tử hiện tại
        current_subsequence.append(arr[index])
        result = backtrack(index + 1, current_sum + arr[index], current_subsequence)
        if result:
            return result
        current_subsequence.pop()
        
        return None
    
    return backtrack(0, 0, [])

def find_all_subsequences(arr, k):
    """
    Tìm tất cả các dãy con có tổng bằng k và trả về dãy có thứ tự từ điển nhỏ nhất
    """
    n = len(arr)
    result = []
    
    def backtrack(index, current_sum, current_subsequence):
        if current_sum == k:
            result.append(current_subsequence[:])
            return
        
        if index >= n or current_sum > k:
            return
        
        # Không lấy phần tử hiện tại
        backtrack(index + 1, current_sum, current_subsequence)
        
        # Lấy phần tử hiện tại
        current_subsequence.append(arr[index])
        backtrack(index + 1, current_sum + arr[index], current_subsequence)
        current_subsequence.pop()
    
    backtrack(0, 0, [])
    
    # Trả về dãy con có thứ tự từ điển nhỏ nhất
    return min(result) if result else None

# Ví dụ sử dụng
if __name__ == "__main__":
    arr = [1, 2, 3, 4, 5]
    k = 5
    
    # Phương pháp 1: Tìm dãy con đầu tiên (thứ tự từ điển nhỏ nhất)
    result1 = find_min_lexicographic_subsequence(arr, k)
    print(f"Dãy con có tổng = {k} (phương pháp 1): {result1}")
    
    # Phương pháp 2: Tìm tất cả rồi chọn nhỏ nhất
    result2 = find_all_subsequences(arr, k)
    print(f"Dãy con có tổng = {k} (phương pháp 2): {result2}")
    
    # Test với mảng khác
    arr2 = [2, 1, 4, 3, 5]
    k2 = 6
    result3 = find_min_lexicographic_subsequence(arr2, k2)
    print(f"Dãy con có tổng = {k2}: {result3}")