# Lambda Promise Cascade
![aws lambda promise cascade](https://github.com/ratmach/AWSLambdaPromiseCascade/blob/master/icon.png?raw=true)

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
from lambda_promised_cascade import lambda_promise, lambda_handler, LambdaPromise


@lambda_promise()
def some_function(arg0, arg1, arg2):
    print(arg0, arg1, arg2)

@lambda_promise(pass_promise_object=True)
def some_function_callback(promise):
    print("arguments were printed")

@lambda_promise(pass_promise_object=True)
def some_function_error_logging(promise):
    print(f"error occurred {promise.result}")


promise_obj = LambdaPromise(
    arn="arn:aws:lambda:us-east-2:123456789012:function:",
    function_name="some_function",
    payload=dict(
        arg0="somebody",
        arg1="once",
        arg2="told me"
    )
).then(
        LambdaPromise(
            arn="arn:aws:lambda:us-east-2:123456789012:function:",
            function_name="some_function_callback"
        )
).catch(
        LambdaPromise(
            arn="arn:aws:lambda:us-east-2:123456789012:function:",
            function_name="some_function_error_logging"
        )
)
promise_obj.async_proceed()

@lambda_handler
def main(event, context):
    pass
```

after `some_function` is called `some_function_callback` will be invoked, if there were any errors during the execution `some_function_error_logging` will be invoked with the error

functions that are invoked via `async_proceed()` should be wrapped w/ `@lambda_promise` decorator
`@lambda_promise` parameters:
- `ignore_result` should result of the function invocation be stored in promise shared memory
- `pass_promise_object` should promise object be passed to function as the first parameter
- `function_name` optional custom name for the function if ignored `{function.__module__}.{function.__name__}` will be used
- `pass_context`

`callback_*` functions must have `invoked_from` parameter set
##### passing promise for a callback:

```python
from lambda_promised_cascade import lambda_promise, lambda_handler, LambdaPromise


@lambda_promise(ignore_result=False, pass_promise_object=False)
def some_function(arg0, arg1, arg2):
    print(arg0, arg1, arg2)


@lambda_promise(ignore_result=True, pass_promise_object=True)
def some_other_function(promise, arg0, arg1, arg2, invoked_from=None):
    print(f"some other function was called from {invoked_from} arguments:", arg0, arg1, arg2)

@lambda_promise(pass_promise_object=True)
def some_function_callback(promise):
    print("arguments were printed")

@lambda_promise(pass_promise_object=True)
def some_function_error_logging(promise):
    print("error occured during printing")


promise_object = LambdaPromise(
    arn="arn:aws:lambda:us-east-2:123456789012:function:",
    function_name="some_function",
    payload=dict(
        arg0="somebody",
        arg1="once",
        arg2="told me"
    )
).then(
    LambdaPromise(
        arn="arn:aws:lambda:us-east-2:123456789012:function:",
        function_name="some_function"
    ).then(LambdaPromise(
        arn="arn:aws:lambda:us-east-2:123456789012:function:",
        function_name="some_function_callback"
    ))
).catch(LambdaPromise(
        arn="arn:aws:lambda:us-east-2:some_function_error_logging:function:",
        function_name="some_function_callback"
))
promise_object.async_proceed()

@lambda_handler
def main(event, context):
    pass
```

##### multiple promises:
```python
from lambda_promised_cascade import lambda_promise, lambda_handler, LambdaPromise


@lambda_promise(pass_promise_object=False)
def some_function(arg0, arg1, arg2, invoked_from=None):
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

@lambda_handler
def main(event, context):
    pass
```
using `then()` multiple times allows for a promise to have multiple callbacks (invocation order is maintained)
#### lambda payload structure:
```json
{"payload": {"payload passed to the promise": "in a form of a dictionary"},
"command": "custom or generated function name",
"invoked_lambda_uid": "promise uuid"}
```
##### Zappa:
lambda payload structure is zappa compliant in order to use it w/ zappa simply omit `@lambda_handler` decorator and let zappa handle events

#### using shared_memory as a standalone:
shared_memory allows data to be shared through lambdas with minimal headache
each `SharedMemory` object acts essentially as a memory page, with unique uuid identifier
in order to access said memory one must have uuid identifier
```python
from lambda_promised_cascade import SharedMemory
import json

shared_memory = SharedMemory()
shared_memory.some_variable = "value"
shared_memory["some_value"] = json.dumps({"something": "that is", "json": "encodable"})

other_shared_memory = SharedMemory(shared_memory.uid)
print(other_shared_memory.some_variable)
print(json.loads(other_shared_memory["some_value"].decode("utf-8")))
```