import json

import boto3
from uuid import uuid4

from .memory import SharedMemory


class LambdaPromise:
    def __init__(self, uid=None, arn=None, function_name=None, payload=None, callback_arns=None,
                 callback_failed_arns=None):
        self.uid = uid or str(uuid4()).replace("-", "")
        self.shared_memory = SharedMemory(uid)
        if not uid:
            self.arn = arn
            self.function_name = function_name
            self.callback_arns = callback_arns or []
            self.callback_failed_arns = callback_failed_arns or []
            self.payload = payload or {}
            self.save_state()
        else:
            data = json.loads(self.shared_memory.data.decode("utf-8"))
            self.arn = data["arn"]
            self.function_name = data["function_name"]
            self.callback_arns = data["callback_arns"]
            self.callback_failed_arns = data["callback_failed_arns"]
            self.payload = data["payload"]

    def then(self, next_promise):
        self.callback_arns.append(next_promise.uid)
        self.save_state()

    def catch(self, next_promise):
        self.callback_failed_arns.append(next_promise.uid)
        self.save_state()
        return self

    def async_proceed(self):
        """
        requires function to be wrapped with @lambda_promise
        :return:
        """
        payload = self.payload
        client = boto3.client("lambda")
        client.invoke(
            FunctionName=self.arn,
            InvocationType='Event',
            Payload=self.prepare_payload(payload, self.function_name),
            Qualifier='string'
        )

    def invoke_callbacks(self):
        if not self.callback_arns:
            return
        client = boto3.client("lambda")
        for function_name in self.callback_arns:
            client.invoke(
                FunctionName=self.arn,
                InvocationType='Event',
                Payload=self.prepare_payload({}, function_name),
                Qualifier='string'
            )

    def invoke_callback_fails(self, reason):
        self.set_result({"error": reason})
        if not self.callback_failed_arns:
            return
        client = boto3.client("lambda")
        for function_name in self.callback_failed_arns:
            client.invoke(
                FunctionName=self.arn,
                InvocationType='Event',
                Payload=self.prepare_payload({}, function_name),
                Qualifier='string'
            )

    def prepare_payload(self, payload, function_name):
        return json.dumps({"command": function_name, "payload": payload, "invoked_lambda_uid": self.uid}).encode(
            "utf-8")

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
                "payload": self.payload, "function_name": self.function_name}

    @property
    def result(self):
        return self.shared_memory.result
