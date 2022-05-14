from utils.promise import LambdaPromise


def lambda_promise(ignore_result=False):
    def func(f):
        def wrap(invoked_lambda_uid=None, *args, **kwargs):
            promise = LambdaPromise(invoked_lambda_uid)
            try:
                result = f(promise, *args, **kwargs)
                promise.invoke_callbacks()
                if not ignore_result:
                    promise.set_result(result)
                return result
            except Exception as e:
                promise.invoke_callback_fails(e)

        return wrap

    return func
