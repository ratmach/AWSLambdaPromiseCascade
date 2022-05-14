from utils.promise import LambdaPromise


def lambda_promise():
    def func(f):
        def wrap(uid=None, *args, **kwargs):
            promise = LambdaPromise(uid)
            try:
                result = f(*args,**kwargs)
                return result
            except Exception as e:
                pass
            # TODO invoke
        return wrap

    return func
