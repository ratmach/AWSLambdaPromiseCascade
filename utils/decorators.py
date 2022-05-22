import logging

from utils.exception import LambdaPromiseException
from utils.promise import LambdaPromise

known_promises = {}

logger = logging.getLogger(__name__)


def lambda_promise(ignore_result=False, pass_promise_object=False, function_name=None, pass_context=None):
    def __(func):
        known_promises[function_name or ".".join((func.__module__, func.__name__,))] = lambda event, context: wrap(
            event, context)

        def wrap(event, context):
            invoked_lambda_uid = event.pop("invoked_lambda_uid", None)
            if not invoked_lambda_uid:
                raise LambdaPromiseException("[lambda_promise] 'invoked_lambda_uid' parameter not set")
            promise = LambdaPromise(invoked_lambda_uid)
            params = event
            if pass_context:
                params.update({"context": context})
            if pass_promise_object:
                params.update({"promise": promise})
            try:
                result = func(**params)
                promise.invoke_callbacks()
                if not ignore_result:
                    promise.set_result(result)
                return result
            except Exception as e:
                promise.invoke_callback_fails(e)

        return wrap

    return __


def lambda_handler(parameter_name="command"):
    def __(func):
        def wrap(event, context):
            function_name = event.pop(parameter_name, None)
            if not function_name:
                logger.warning("[lambda_handler] command parameter not set")
            else:
                function_instance = known_promises.get(function_name, None)
                if not function_instance:
                    logger.warning("[lambda_handler] function %s cannot be found", function_name)
                else:
                    try:
                        result = function_instance(event, context)
                    except LambdaPromiseException as e:
                        logger.error(e)
                        raise
            return func(event, context)

        return wrap

    return __
