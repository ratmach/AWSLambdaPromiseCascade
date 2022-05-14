import boto3
from uuid import uuid4

from utils.exception import LambdaPromiseException
from utils.memory import SharedMemory


class LambdaPromise:
    def __init__(self, uid=None, arn=None, payload=None, callback_arns=None, callback_failed_arns=None):
        self.uid = uid or str(uuid4()).replace("-", "")
        self.shared_memory = SharedMemory(uid)
        if not uid:
            self.arn = arn
            self.callback_arns = callback_arns or []
            self.callback_failed_arns = callback_failed_arns or []
            self.payload = payload or {}
        else:
            self.arn = self.shared_memory[uid].arn
            self.callback_arns = self.shared_memory[uid].callback_arn
            self.callback_failed_arns = self.shared_memory[uid].callback_failed_arn
            self.payload = self.shared_memory[uid].payload

    def then(self, next_arn):
        self.callback_arns.append(next_arn)
        self.save_state()
        try:
            pass
        except Exception as e:
            pass
        return self

    def catch(self, next_arn):
        self.callback_failed_arns.append(next_arn)
        self.save_state()
        return self

    def proceed(self):
        client = boto3.client("lambda")
        response = client.invoke(
            FunctionName='string',
            InvocationType='RequestResponse',
            Payload=self.payload.encode("utf-8"),
            Qualifier='string'
        )
        if response.StatusCode == 200:
            pass  # INVOKE callbacks
        else:
            pass  # INVOKE callback_errors

    def async_proceed(self):
        """
        requires function to be wrapped with @lambda_promise
        :return:
        """
        client = boto3.client("lambda")
        response = client.invoke(
            FunctionName='string',
            InvocationType='Event',
            Payload=self.payload.encode("utf-8"),
            Qualifier='string'
        )

    def save_state(self):
        pass

    @property
    def data(self):
        return {"arn": self.arn, "callback_arn": self.callback_arn, "callback_failed_arn": self.callback_failed_arns,
                "payload": self.payload}
