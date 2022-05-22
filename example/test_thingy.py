from utils import lambda_promise


@lambda_promise()
def test_function(param1, param2, param3):
    print("[test_function] invoked w/", param1, param2, param3)
