from utils.promise import LambdaPromise


def lambda_promise():
    def func(f):
        def wrap(uid=None, *args, **kwargs):
            promise = LambdaPromise(uid)
            try:
                result = f(*args, **kwargs)
                promise.invoke_callbacks()
                return result
            except Exception as e:
                promise.invoke_callback_fails(e)

        return wrap

    return func
