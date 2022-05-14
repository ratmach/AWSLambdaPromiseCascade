# Lambda Promise Cascade
### !!! please keep in mind this repository is a work in progress !!!

Python based lambda promise solution using redis

library is a wrapper for lambda function invocation, payload and memory sharing
as well as keeping track of execution status

allowing developers to avoid 15 minute execution limit as well as use serverless for large, distributed task execution

this will only works for AWS for now
## Installation:
## Dependencies:
## Usage:

##### standard usage:
```python
from utils import lambda_promise, LambdaPromise


@lambda_promise()
def some_function(arg0, arg1, arg2):
    print(arg0, arg1, arg2)


def some_function_callback():
    print("arguments were printed")


def some_function_error_logging(e):
    print(f"error occurred {e}")


promise = LambdaPromise(
    arn="arn:aws:lambda:us-east-2:123456789012:function:some_function:",
    payload=dict(
        arg0="somebody",
        arg1="once",
        arg2="told me"
    )
).then("arn:aws:lambda:us-east-2:123456789012:function:some_function_callback:"
       ).catch("arn:aws:lambda:us-east-2:123456789012:function:some_function_error_logging:")
promise.async_proceed()
```

after `some_function` is called `some_function_callback` will be invoked, if there were any errors during the execution `some_function_error_logging` will be invoked with the error

##### passing promise for a callback:

```python
from utils import lambda_promise, LambdaPromise


@lambda_promise()
def some_function(arg0, arg1, arg2):
    print(arg0, arg1, arg2)


@lambda_promise()
def some_other_function(arg0, arg1, arg2):
    print("some other function was called with arguments:", arg0, arg1, arg2)


def some_function_callback():
    print("arguments were printed")


def some_function_error_logging():
    print("error occured during printing")


promise = LambdaPromise(
    arn="arn:aws:lambda:us-east-2:123456789012:function:some_function:",
    payload=dict(
        arg0="somebody",
        arg1="once",
        arg2="told me"
    )
).then(
    LambdaPromise(
        arn="arn:aws:lambda:us-east-2:123456789012:function:some_other_function:"
    ).then("arn:aws:lambda:us-east-2:123456789012:function:some_function_callback:")
).catch("arn:aws:lambda:us-east-2:123456789012:function:some_function_error_logging:")
promise.async_proceed()

```

##### multiple promises:
```python
from utils import lambda_promise, LambdaPromise


@lambda_promise()
def some_function(arg0, arg1, arg2):
    print(arg0, arg1, arg2)


promise = LambdaPromise(
    arn="arn:aws:lambda:us-east-2:123456789012:function:some_function:",
    payload=dict(
        arg0="somebody",
        arg1="once",
        arg2="told me"
    )
).then(
    LambdaPromise(
        arn="arn:aws:lambda:us-east-2:123456789012:function:some_function:",
        payload=dict(
            arg0="the world was",
            arg1="gonna",
            arg2="roll me"
        )
    )
).then(
    LambdaPromise(
        arn="arn:aws:lambda:us-east-2:123456789012:function:some_function:",
        payload=dict(
            arg0="i ain't",
            arg1="the sharpest",
            arg2="tool in the shed"
        )
    )
)
promise.async_proceed()
```
using `then()` multiple times allows for a promise to have multiple callbacks (invocation order is maintained)

##### using shared_memory as a standalone:
shared_memory allows data to be shared through lambdas with minimal headache
each `SharedMemory` object acts essentially as a memory page, with unique uuid identifier
in order to access said memory one must have uuid identifier
```python
from utils import SharedMemory
import json

shared_memory = SharedMemory()
shared_memory.some_variable = "value"
shared_memory["some_value"] = json.dumps({"something": "that is", "json": "encodable"})

other_shared_memory = SharedMemory(shared_memory.uid)
print(other_shared_memory.some_variable)
print(json.loads(other_shared_memory["some_value"].decode("utf-8")))
```