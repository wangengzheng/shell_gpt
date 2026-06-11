from unittest.mock import Mock, patch

from sgpt.function import get_function


def test_get_function_returns_wrapper_for_existing_function():
    """Test that get_function returns a wrapper function when the function exists."""
    # Create a mock function
    mock_func = Mock(return_value="test_result")
    mock_func.__name__ = "test_function"
    
    # Create a mock Function object
    mock_function_obj = Mock()
    mock_function_obj.name = "test_function"
    mock_function_obj.execute = mock_func
    
    # Patch the functions list
    with patch("sgpt.function.functions", [mock_function_obj]):
        result = get_function("test_function")
        
        # Verify it returns a callable
        assert callable(result)
        # Verify it's wrapped
        assert hasattr(result, "__wrapped__")


def test_get_function_filters_kwargs_correctly():
    """Test that the wrapper filters kwargs based on function signature."""
    # Create a function with specific parameters
    def sample_func(param1, param2, param3=None):
        return f"{param1}-{param2}-{param3}"
    
    # Create a mock Function object
    mock_function_obj = Mock()
    mock_function_obj.name = "sample_func"
    mock_function_obj.execute = sample_func
    
    # Patch the functions list
    with patch("sgpt.function.functions", [mock_function_obj]):
        wrapper = get_function("sample_func")
        
        # Call with extra kwargs that should be filtered out
        result = wrapper("a", "b", param3="c", extra_param="should_be_filtered")
        
        # Verify the function was called with only valid parameters
        assert result == "a-b-c"


def test_get_function_raises_error_for_nonexistent_function():
    """Test that get_function raises ValueError when function is not found."""
    # Create a mock Function object with different name
    mock_function_obj = Mock()
    mock_function_obj.name = "existing_function"
    
    # Patch the functions list
    with patch("sgpt.function.functions", [mock_function_obj]):
        try:
            get_function("nonexistent")
            assert False, "Expected ValueError to be raised"
        except ValueError as e:
            assert "Function nonexistent not found" in str(e)


def test_get_function_raises_error_for_empty_functions_list():
    """Test that get_function raises ValueError when functions list is empty."""
    # Patch the functions list to be empty
    with patch("sgpt.function.functions", []):
        try:
            get_function("any_function")
            assert False, "Expected ValueError to be raised"
        except ValueError as e:
            assert "Function any_function not found" in str(e)


def test_get_function_wrapper_preserves_function_metadata():
    """Test that the wrapper preserves the original function's metadata."""
    def original_func(arg1, arg2):
        """Original docstring."""
        return arg1 + arg2
    
    mock_function_obj = Mock()
    mock_function_obj.name = "original_func"
    mock_function_obj.execute = original_func
    
    with patch("sgpt.function.functions", [mock_function_obj]):
        wrapper = get_function("original_func")
        
        # Verify metadata is preserved through wraps decorator
        assert wrapper.__name__ == "original_func"
        assert wrapper.__doc__ == "Original docstring."


def test_get_function_with_multiple_functions_finds_correct_one():
    """Test that get_function finds the correct function among multiple functions."""
    def func_a():
        return "A"
    
    def func_b():
        return "B"
    
    def func_c():
        return "C"
    
    mock_function_a = Mock()
    mock_function_a.name = "func_a"
    mock_function_a.execute = func_a
    
    mock_function_b = Mock()
    mock_function_b.name = "func_b"
    mock_function_b.execute = func_b
    
    mock_function_c = Mock()
    mock_function_c.name = "func_c"
    mock_function_c.execute = func_c
    
    functions_list = [mock_function_a, mock_function_b, mock_function_c]
    
    with patch("sgpt.function.functions", functions_list):
        result_b = get_function("func_b")
        assert result_b() == "B"
        
        result_a = get_function("func_a")
        assert result_a() == "A"


def test_get_function_wrapper_handles_args_and_kwargs():
    """Test that the wrapper correctly handles both *args and **kwargs."""
    def mixed_func(positional, keyword="default"):
        return f"{positional}:{keyword}"
    
    mock_function_obj = Mock()
    mock_function_obj.name = "mixed_func"
    mock_function_obj.execute = mixed_func
    
    with patch("sgpt.function.functions", [mock_function_obj]):
        wrapper = get_function("mixed_func")
        
        # Test with positional args
        result1 = wrapper("value1")
        assert result1 == "value1:default"
        
        # Test with keyword args
        result2 = wrapper("value1", keyword="custom")
        assert result2 == "value1:custom"


def test_get_function_wrapper_filters_invalid_parameters():
    """Test that invalid parameters are properly filtered out."""
    def simple_func(valid_param):
        return valid_param
    
    mock_function_obj = Mock()
    mock_function_obj.name = "simple_func"
    mock_function_obj.execute = simple_func
    
    with patch("sgpt.function.functions", [mock_function_obj]):
        wrapper = get_function("simple_func")
        
        # Call with many invalid kwargs
        result = wrapper(
            "valid_value",
            invalid1="should_filter",
            invalid2="also_filter",
            another_invalid="filter_this_too"
        )
        
        # Should only pass valid_param
        assert result == "valid_value"


def test_get_function_case_sensitive_name_matching():
    """Test that function name matching is case-sensitive."""
    mock_function_obj = Mock()
    mock_function_obj.name = "MyFunction"
    mock_function_obj.execute = Mock(return_value="result")
    
    with patch("sgpt.function.functions", [mock_function_obj]):
        # Exact match should work
        result = get_function("MyFunction")
        assert callable(result)
        
        # Different case should fail
        try:
            get_function("myfunction")
            assert False, "Expected ValueError to be raised"
        except ValueError as e:
            assert "Function myfunction not found" in str(e)
        
        try:
            get_function("MYFUNCTION")
            assert False, "Expected ValueError to be raised"
        except ValueError as e:
            assert "Function MYFUNCTION not found" in str(e)
