from utils.promise import LambdaPromise


def lambda_promise(ignore_result=False, pass_promise_object=False):
    def func(f):
        def wrap(invoked_lambda_uid=None, *args, **kwargs):
            promise = LambdaPromise(invoked_lambda_uid)
            try:
                if pass_promise_object:
                    result = f(promise, *args, **kwargs)
                else:
                    result = f(promise, *args, **kwargs)
                promise.invoke_callbacks()
                if not ignore_result:
                    promise.set_result(result)
                return result
            except Exception as e:
                promise.invoke_callback_fails(e)

        return wrap

    return func
