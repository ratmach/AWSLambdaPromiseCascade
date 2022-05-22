import json

import boto3
from uuid import uuid4

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
            self.save_state()
        else:
            data = json.loads(self.shared_memory.data.decode("utf-8"))
            self.arn = data["arn"]
            self.callback_arns = data["callback_arns"]
            self.callback_failed_arns = data["callback_failed_arns"]
            self.payload = data["payload"]

    def then(self, next_arn):
        self.callback_arns.append(next_arn)
        self.save_state()

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
            self.invoke_callbacks()
        else:
            self.invoke_callback_fails(response.FunctionError)

    def async_proceed(self):
        """
        requires function to be wrapped with @lambda_promise
        :return:
        """
        payload = self.payload
        payload["invoked_lambda_uid"] = self.uid
        client = boto3.client("lambda")
        client.invoke(
            FunctionName=self.arn,
            InvocationType='Event',
            Payload=json.dumps(payload).encode("utf-8"),
            Qualifier='string'
        )

    def invoke_callbacks(self):
        if not self.callback_arns:
            return
        client = boto3.client("lambda")
        payload = {"invoked_from": self.uid}
        for arn in self.callback_arns:
            client.invoke(
                FunctionName=arn,
                InvocationType='Event',
                Payload=json.dumps(payload).encode("utf-8"),
                Qualifier='string'
            )

    def invoke_callback_fails(self, reason):
        self.set_result({"error": reason})
        if not self.callback_failed_arns:
            return
        client = boto3.client("lambda")
        payload = {"invoked_from": self.uid}
        for arn in self.callback_failed_arns:
            client.invoke(
                FunctionName=arn,
                InvocationType='Event',
                Payload=json.dumps(payload).encode("utf-8"),
                Qualifier='string'
            )

    def save_state(self):
        self.shared_memory.data = json.dumps(self.data)

    def set_result(self, result):
        if not result:
            result = "None"
        if isinstance(result, dict):
            result = json.dumps(result)
        self.shared_memory.result = result

    @property
    def data(self):
        return {"arn": self.arn, "callback_arns": self.callback_arns, "callback_failed_arns": self.callback_failed_arns,
                "payload": self.payload}

    @property
    def result(self):
        return self.shared_memory.result
