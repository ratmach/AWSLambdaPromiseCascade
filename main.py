from utils import LambdaPromise
from utils.decorators import lambda_handler, lambda_promise
from example.test_thingy import test_function


@lambda_handler()
def main(event, context):
    pass


if __name__ == '__main__':
    promise = LambdaPromise(
        arn="example.test_thingy.test_function",
    )
    main({"command": "example.test_thingy.test_function", "param1": 1, "param2": 2, "param3": 3,
          "invoked_lambda_uid": promise.uid}, None)
