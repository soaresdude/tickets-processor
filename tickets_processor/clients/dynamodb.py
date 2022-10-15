from dataclasses import asdict
from typing import Any

import boto3

from tickets_processor.dtos.tickets import TicketInfo


dynamodb = boto3.resource("dynamodb", region_name="us-east-1", endpoint_url="http://dynamodb-local:8000")


class DynamoDBClient:
    dynamo_sdk: dynamodb = dynamodb
    table: Any = None

    def _get_or_create_table(self, table_name: str):

        if not self.table:
            table = self.dynamo_sdk.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        "AttributeName": "key",
                        "KeyType": "HASH"
                    },
                    {
                        "AttributeName": "id",
                        "KeyType": "RANGE"
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'key',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'N'
                    },
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5
                }
            )
            self.table = table

        return self.table

    def save_ticket(self, ticket_info: TicketInfo):
        table = self._get_or_create_table("tickets")

        return table.put_item(
            Item=asdict(ticket_info)
        )

